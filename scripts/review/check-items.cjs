// scripts/review/check-items.cjs
//
// Programmatically tick (or untick) action-item checkboxes on a
// site-review tracking issue. Reusable across review batches: dispatch
// the workflow, name the items, and the matching `- [ ]` lines flip to
// `- [x]` (or back) via a single body PATCH.
//
// Triggered by .github/workflows/site-review-check.yml. Writes only to
// GitHub Issues (issue body + an optional audit comment). No secrets
// beyond the Actions GITHUB_TOKEN.
//
// IMPORTANT — interaction with issue-lifecycle.cjs:
//   The publish workflow regenerates an issue body straight from
//   `reviews/<date>-synthesis.md` whenever it re-runs for the SAME date,
//   re-emitting every item as `- [ ]`. That wipes checks made here. So:
//     - Across review batches (new date), a `- [x]` is durable: the
//       lifecycle's carry-forward only repeats unchecked items.
//     - Against a same-date republish, it is NOT durable: also resolve
//       the item in the synthesis source if you need it to survive.
//   See scripts/review/README.md §Checking items off programmatically.

const REPORT_LABEL = 'site-review';

// Matches a GitHub task-list line, capturing indent, current state, and
// label. Any indent is allowed (more permissive than the lifecycle
// parser, which ignores indented sub-items).
const TASK_RE = /^(\s*)-\s+\[([ xX])\]\s+(.+)$/;

function parseBool(v, dflt) {
  const s = (v || '').trim().toLowerCase();
  if (s === '') return dflt;
  return s === 'true' || s === '1' || s === 'yes';
}

// Split a multiline / comma-separated input into trimmed selectors.
function parseSelectors(raw) {
  return (raw || '')
    .split(/[\n,]/)
    .map(s => s.trim())
    .filter(Boolean);
}

// Build the checklist model: one entry per task-list line in the body,
// numbered 1-based in document order.
function indexChecklist(body) {
  const lines = (body || '').split('\n');
  const items = [];
  lines.forEach((line, lineIdx) => {
    const m = line.match(TASK_RE);
    if (m) {
      items.push({
        lineIdx,
        index: items.length + 1,
        indent: m[1],
        checked: m[2].toLowerCase() === 'x',
        label: m[3].trim(),
      });
    }
  });
  return { lines, items };
}

// Resolve each selector to checklist entries. Pure integers match by
// 1-based index; everything else is a case-insensitive substring match
// on the label. Returns { matched: Set<lineIdx>, unmatched: string[] }.
function resolveSelectors(selectors, items) {
  const matched = new Map(); // lineIdx -> item
  const unmatched = [];
  for (const sel of selectors) {
    let hits = [];
    if (/^\d+$/.test(sel)) {
      const n = parseInt(sel, 10);
      hits = items.filter(it => it.index === n);
    } else {
      const needle = sel.toLowerCase();
      hits = items.filter(it => it.label.toLowerCase().includes(needle));
    }
    if (hits.length === 0) {
      unmatched.push(sel);
    } else {
      for (const it of hits) matched.set(it.lineIdx, it);
    }
  }
  return { matched, unmatched };
}

async function resolveIssueNumber({ github, context, requested }) {
  if (requested) {
    const n = parseInt(String(requested).replace(/^#/, ''), 10);
    if (!Number.isInteger(n)) {
      throw new Error(`Invalid issue input: ${requested}`);
    }
    return n;
  }
  // Default: the latest open site-review issue (the live tracking issue).
  const issues = await github.paginate(github.rest.issues.listForRepo, {
    ...context.repo,
    state: 'open',
    labels: REPORT_LABEL,
    sort: 'created',
    direction: 'desc',
    per_page: 50,
  });
  const live = issues.find(i => !i.pull_request);
  if (!live) {
    throw new Error(
      `No open issue with the "${REPORT_LABEL}" label and no explicit issue input.`
    );
  }
  return live.number;
}

async function run({ github, context, core }) {
  const selectors = parseSelectors(process.env.ITEMS);
  const wantChecked = (process.env.STATE || 'checked').trim().toLowerCase() !== 'unchecked';
  const dryRun = parseBool(process.env.DRY_RUN, false);
  const doComment = parseBool(process.env.COMMENT, true);

  if (selectors.length === 0) {
    core.setFailed('No items supplied. Pass `items` (indices and/or label substrings).');
    return;
  }

  const issueNumber = await resolveIssueNumber({
    github,
    context,
    requested: (process.env.ISSUE || '').trim(),
  });

  const { data: issue } = await github.rest.issues.get({
    ...context.repo,
    issue_number: issueNumber,
  });

  const { lines, items } = indexChecklist(issue.body);
  if (items.length === 0) {
    core.setFailed(`Issue #${issueNumber} has no task-list checkboxes to flip.`);
    return;
  }

  const { matched, unmatched } = resolveSelectors(selectors, items);

  if (matched.size === 0) {
    core.setFailed(
      `None of the supplied selectors matched a checkbox on #${issueNumber}: ${selectors.join(', ')}`
    );
    return;
  }

  const mark = wantChecked ? 'x' : ' ';
  const verb = wantChecked ? 'Checked' : 'Unchecked';
  const flipped = [];
  const noop = [];

  for (const [lineIdx, it] of matched) {
    if (it.checked === wantChecked) {
      noop.push(it);
      continue;
    }
    lines[lineIdx] = `${it.indent}- [${mark}] ${it.label}`;
    flipped.push(it);
  }

  // Report to the job log regardless of dry-run.
  core.info(`Issue #${issueNumber}: ${issue.title}`);
  for (const it of flipped) core.info(`  ${verb}: [${it.index}] ${it.label}`);
  for (const it of noop) core.info(`  Already ${wantChecked ? 'checked' : 'unchecked'}: [${it.index}] ${it.label}`);
  for (const sel of unmatched) core.warning(`  No match for selector: "${sel}"`);

  core.setOutput('flipped', String(flipped.length));
  core.setOutput('issue_number', String(issueNumber));

  if (dryRun) {
    core.info('Dry run: no changes written.');
    return;
  }
  if (flipped.length === 0) {
    core.info('Nothing to change (all matched items already in target state).');
    return;
  }

  await github.rest.issues.update({
    ...context.repo,
    issue_number: issueNumber,
    body: lines.join('\n'),
  });
  core.info(`Updated #${issueNumber}: flipped ${flipped.length} item(s).`);

  if (doComment) {
    const body = [
      `${verb} ${flipped.length} item(s) via \`site-review-check\`:`,
      '',
      ...flipped.map(it => `- ${wantChecked ? '[x]' : '[ ]'} ${it.label}`),
      ...(unmatched.length
        ? ['', `Unmatched selectors (no change): ${unmatched.map(s => `\`${s}\``).join(', ')}`]
        : []),
    ].join('\n');
    await github.rest.issues.createComment({
      ...context.repo,
      issue_number: issueNumber,
      body,
    });
  }
}

module.exports = {
  run,
  parseSelectors,
  indexChecklist,
  resolveSelectors,
  TASK_RE,
};
