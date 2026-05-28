// scripts/review/issue-lifecycle.cjs
//
// Opens (or updates in place) a single tracking issue per site-review batch.
// Closes the prior open site-review issue with a templated comment.
// Carries forward unchecked action items and explicit deferral notes from
// the prior issue into the new one.
//
// Triggered by .github/workflows/site-review-publish.yml. Reads only the
// repository working tree and writes only to GitHub Issues. No external
// secrets needed.
//
// See scripts/review/README.md for the canonical file layout and the
// expected synthesis-report structure.

const fs = require('node:fs');

const REPORT_LABEL = 'site-review';
const NEEDS_DECISION_LABEL = 'needs-decision';
const REPORT_DIRS = ['critiques', 'evaluations', 'reviews'];

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function readIfExists(p) {
  try {
    return fs.readFileSync(p, 'utf8');
  } catch (e) {
    if (e.code === 'ENOENT') return null;
    throw e;
  }
}

function reportPaths(date) {
  return {
    craft: `critiques/critique-${date}.md`,
    alignment: `critiques/critique-${date}-alignment.md`,
    hiring: `evaluations/hiring-eval-${date}.md`,
    synthesis: `reviews/${date}-synthesis.md`,
  };
}

// Latest YYYY-MM-DD prefix found across the canonical directories.
function detectLatestDate() {
  const dates = new Set();
  for (const dir of REPORT_DIRS) {
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      const m = name.match(/(\d{4}-\d{2}-\d{2})/);
      if (m) dates.add(m[1]);
    }
  }
  if (dates.size === 0) return null;
  return [...dates].sort().pop();
}

// Pull `- [ ]` (unchecked) lines from markdown, tagging each with the most
// recent `### Tier N ...` heading. Stops attributing once a non-tier `##`
// heading appears.
function parseChecklist(markdown) {
  const lines = (markdown || '').split('\n');
  const items = [];
  let currentTier = null;
  for (const line of lines) {
    const tierMatch = line.match(/^###\s+(Tier\s+\d[^\n]*)/i);
    if (tierMatch) {
      currentTier = tierMatch[1].trim();
      continue;
    }
    if (/^##\s/.test(line)) {
      currentTier = null;
      continue;
    }
    const itemMatch = line.match(/^-\s+\[\s\]\s+(.+)$/);
    if (itemMatch) {
      items.push({ tier: currentTier, label: itemMatch[1].trim() });
    }
  }
  return items;
}

// Comment lines beginning with `defer:` or `wontfix:` are treated as
// per-item lifecycle annotations. The reason is the rest of the line.
async function scanComments({ github, context, issueNumber }) {
  const comments = await github.paginate(github.rest.issues.listComments, {
    ...context.repo,
    issue_number: issueNumber,
  });
  const out = [];
  for (const c of comments) {
    for (const line of (c.body || '').split('\n')) {
      const m = line.match(/^(defer|wontfix):\s*(.+)/i);
      if (m) {
        out.push({
          kind: m[1].toLowerCase(),
          reason: m[2].trim(),
          author: c.user && c.user.login,
          at: c.created_at,
        });
      }
    }
  }
  return out;
}

async function findPriorIssue({ github, context }) {
  const issues = await github.paginate(github.rest.issues.listForRepo, {
    ...context.repo,
    state: 'open',
    labels: REPORT_LABEL,
    sort: 'created',
    direction: 'desc',
    per_page: 50,
  });
  // Filter out pull requests (the issues API includes them).
  return issues.find(i => !i.pull_request) || null;
}

async function ensureLabel({ github, context, name, color, description }) {
  try {
    await github.rest.issues.getLabel({ ...context.repo, name });
  } catch (e) {
    if (e.status === 404) {
      await github.rest.issues.createLabel({
        ...context.repo,
        name,
        color,
        description,
      });
    } else {
      throw e;
    }
  }
}

function buildIssueBody({
  date,
  notes,
  paths,
  presentReports,
  contents,
  carriedForward,
  deferrals,
  priorIssue,
}) {
  const synthesisMarkdown = contents.synthesis;
  const lines = [];

  lines.push(`Reports for **${date}** are committed.`);
  if (notes) {
    lines.push('');
    lines.push(`> ${notes}`);
  }
  lines.push('');

  lines.push('## Reports in this run');
  for (const [key, p] of Object.entries(paths)) {
    const mark = presentReports.has(key) ? '✓' : '— *(missing)*';
    lines.push(`- ${mark} \`${p}\``);
  }
  lines.push('');

  lines.push('## Action items');
  lines.push('');
  if (synthesisMarkdown) {
    const checklist = parseChecklist(synthesisMarkdown);
    if (checklist.length > 0) {
      lines.push(
        'Check items as you ship them. To defer or skip an item, leave a comment on this issue starting with `defer: <reason>` or `wontfix: <reason>`. The next review will pick those notes up.'
      );
      lines.push('');
      const byTier = new Map();
      for (const item of checklist) {
        const key = item.tier || 'Untiered';
        if (!byTier.has(key)) byTier.set(key, []);
        byTier.get(key).push(item);
      }
      const order = [...byTier.keys()].sort((a, b) => {
        const ta = a.match(/Tier\s+(\d)/i);
        const tb = b.match(/Tier\s+(\d)/i);
        if (ta && tb) return parseInt(ta[1], 10) - parseInt(tb[1], 10);
        if (ta) return -1;
        if (tb) return 1;
        return a.localeCompare(b);
      });
      for (const tier of order) {
        lines.push(`### ${tier}`);
        for (const item of byTier.get(tier)) {
          lines.push(`- [ ] ${item.label}`);
        }
        lines.push('');
      }
    } else {
      lines.push(
        '*Synthesis report present but no `- [ ]` checklist items found under `### Tier N` headings. Edit this section manually, or update the synthesis to include a tiered action list (see `scripts/review/README.md`).*'
      );
      lines.push('');
    }
  } else {
    lines.push(
      `*No synthesis report at \`${paths.synthesis}\`. Generate one (see \`scripts/review/README.md\`) and re-run, or fill this section by hand.*`
    );
    lines.push('');
  }

  if (priorIssue && carriedForward.length > 0) {
    lines.push(`## Carried forward from #${priorIssue.number}`);
    lines.push('');
    lines.push(
      `These items were unchecked in [the prior review](${priorIssue.html_url}). They are repeated here so they do not slip between runs.`
    );
    lines.push('');
    for (const item of carriedForward) {
      const suffix = item.tier ? ` *(${item.tier})*` : '';
      lines.push(`- [ ] ${item.label}${suffix}`);
    }
    lines.push('');
  }

  if (deferrals.length > 0) {
    lines.push('## Explicitly deferred (from prior reviews)');
    lines.push('');
    for (const d of deferrals) {
      const dateStr = (d.at || '').slice(0, 10);
      const who = d.author ? `@${d.author}` : 'unknown';
      lines.push(`- **${d.kind}** by ${who}${dateStr ? ` on ${dateStr}` : ''}: ${d.reason}`);
    }
    lines.push('');
  }

  lines.push('---');
  lines.push('');
  lines.push(
    'Generated by `.github/workflows/site-review-publish.yml`. Operator notes: `scripts/review/README.md`.'
  );

  return lines.join('\n');
}

async function run({ github, context, core }) {
  const requestedDate = (process.env.REPORT_DATE || '').trim();
  const date = requestedDate || detectLatestDate() || todayISO();
  const notes = (process.env.RUN_NOTES || '').trim();
  const paths = reportPaths(date);

  const presentReports = new Set();
  const contents = {};
  for (const [key, p] of Object.entries(paths)) {
    const md = readIfExists(p);
    if (md !== null) {
      presentReports.add(key);
      contents[key] = md;
    }
  }

  if (presentReports.size === 0) {
    core.setFailed(
      `No reports found for date ${date}. Expected at least one of: ${Object.values(paths).join(', ')}.`
    );
    return;
  }
  core.info(
    `Date: ${date}. Found ${presentReports.size}/${Object.keys(paths).length} reports: ${[...presentReports].join(', ')}.`
  );

  await ensureLabel({
    github,
    context,
    name: REPORT_LABEL,
    color: '5319e7',
    description: 'Multi-agent page review lifecycle',
  });
  await ensureLabel({
    github,
    context,
    name: NEEDS_DECISION_LABEL,
    color: 'fbca04',
    description: 'Awaits author decisions on review findings',
  });

  const priorIssue = await findPriorIssue({ github, context });
  let carriedForward = [];
  let deferrals = [];
  if (priorIssue) {
    core.info(`Prior open issue: #${priorIssue.number} (${priorIssue.title}).`);
    carriedForward = parseChecklist(priorIssue.body || '');
    deferrals = await scanComments({
      github,
      context,
      issueNumber: priorIssue.number,
    });
    core.info(
      `Prior issue contains ${carriedForward.length} unchecked item(s) and ${deferrals.length} deferral note(s).`
    );
  } else {
    core.info('No prior open site-review issue.');
  }

  const body = buildIssueBody({
    date,
    notes,
    paths,
    presentReports,
    contents,
    carriedForward,
    deferrals,
    priorIssue,
  });
  const title = `Site review: ${date}`;

  // Idempotency: if an issue with this exact title already exists (any
  // state), update it in place rather than open a duplicate.
  const existing = await github.paginate(github.rest.issues.listForRepo, {
    ...context.repo,
    state: 'all',
    labels: REPORT_LABEL,
    per_page: 100,
  });
  const dupe = existing.find(i => !i.pull_request && i.title === title);

  let issue;
  if (dupe) {
    core.info(`Issue for ${date} already exists at #${dupe.number}. Updating in place.`);
    const updated = await github.rest.issues.update({
      ...context.repo,
      issue_number: dupe.number,
      body,
      state: 'open',
    });
    issue = updated.data;
  } else {
    const created = await github.rest.issues.create({
      ...context.repo,
      title,
      body,
      labels: [REPORT_LABEL, NEEDS_DECISION_LABEL],
    });
    issue = created.data;
    core.info(`Opened new issue #${issue.number}: ${issue.html_url}`);
  }
  core.setOutput('issue_url', issue.html_url);
  core.setOutput('issue_number', String(issue.number));

  // Close the prior issue (if any and distinct from the one we just touched).
  if (priorIssue && priorIssue.number !== issue.number) {
    const priorBody = priorIssue.body || '';
    const completedCount = (priorBody.match(/^-\s+\[x\]/gim) || []).length;
    const closingComment = [
      `Superseded by #${issue.number}.`,
      '',
      `- Completed since last review: **${completedCount}** item(s)`,
      `- Carried forward: **${carriedForward.length}** item(s)`,
      `- Explicit deferrals captured: **${deferrals.length}** note(s)`,
      '',
      `Reopen by editing #${issue.number} if anything here needs revisiting.`,
    ].join('\n');
    await github.rest.issues.createComment({
      ...context.repo,
      issue_number: priorIssue.number,
      body: closingComment,
    });
    await github.rest.issues.update({
      ...context.repo,
      issue_number: priorIssue.number,
      state: 'closed',
      state_reason: 'completed',
    });
    core.info(`Closed prior issue #${priorIssue.number}.`);
  }
}

module.exports = {
  run,
  parseChecklist,
  detectLatestDate,
  reportPaths,
  buildIssueBody,
  todayISO,
};
