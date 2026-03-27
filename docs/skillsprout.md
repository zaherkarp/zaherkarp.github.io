# SkillSprout — O*NET Career Trajectory Explorer

Interactive, client-side career trajectory engine that uses the full O*NET 28.3
database (1,016 occupations, 65 skill/knowledge dimensions) to generate
**Ready Now**, **Trainable**, and **Long-Term Reskill** job transition
recommendations with skill gap analysis and training path suggestions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  /skillsprout/index.astro  ─  page shell (Astro + CSS)         │
│  └─ <SkillSproutDemo client:load />  ─  React interactive UI   │
│       ├─ callApi()  ──────────→  skillsprout-api.ts             │
│       │                           (session state, pagination)   │
│       │                           └─ getCareerTrajectories()    │
│       │                               skillsprout-engine.ts     │
│       │                               (IDF matching, scoring)   │
│       │                               └─ occupations[]          │
│       │                                   onet-occupations.ts   │
│       │                                   └─ onet-full.json     │
│       │                                       (1,016 records)   │
│       └─ <TestSuiteRunner />  ─  in-browser test runner         │
│            └─ skillsprout-test-cases.ts  (55 test cases)        │
└─────────────────────────────────────────────────────────────────┘
```

All matching runs **entirely in the browser** — no data leaves the user's
machine, no API keys needed.

## Data Pipeline

### Source
O*NET Database 28.3 (CC BY 4.0)
https://www.onetcenter.org/database.html

### Processing Script
```bash
# Download and extract O*NET text files
curl -sL https://www.onetcenter.org/dl_files/database/db_28_3_text.zip -o /tmp/onet.zip
unzip /tmp/onet.zip -d /tmp/onet_data

# Process into compact JSON
node scripts/process-onet.mjs /tmp/onet_data/db_28_3_text/
# → writes src/data/onet-full.json (~709 KB)
```

The script (`scripts/process-onet.mjs`) reads four O*NET text files:

| File | Rows | What it provides |
|------|------|-----------------|
| Occupation Data.txt | 1,016 | O*NET-SOC codes, titles, descriptions |
| Skills.txt | 61,110 | 35 skills rated by importance per occupation |
| Knowledge.txt | 57,618 | 33 knowledge areas rated by importance per occupation |
| Job Zones.txt | 923 | Job zone (1-5) per occupation |

Processing steps:
1. Parse tab-delimited files
2. Filter to Importance (IM) scale ratings ≥ 2.75
3. Merge skills + knowledge into a single ranked list
4. Keep top 15 per occupation (sorted by importance)
5. Assign SOC major group category
6. Write compact JSON (no descriptions, no pay data — keeps bundle small)

### Output Schema
```typescript
{
  version: string;        // "28.3"
  source: string;         // Attribution URL
  license: string;        // "CC BY 4.0"
  stats: { occupations: number; uniqueSkills: number; categories: number };
  occupations: Array<{
    code: string;         // "15-1252.00"
    title: string;        // "Software Developers"
    zone: number;         // 1-5
    category: string;     // "Computer & Mathematical"
    skills: Array<{
      name: string;       // "Computers and Electronics"
      importance: number; // 1.0–5.0 (O*NET IM scale)
    }>;
  }>;
}
```

## Matching Algorithm

### Skill Overlap Score
Weighted Jaccard similarity using **inverse document frequency (IDF)**:

```
score = Σ(shared skills × IDF weight) / Σ(union skills × IDF weight)
```

IDF penalizes ubiquitous skills ("Speaking", "Active Listening") and amplifies
specialized ones ("Medicine and Dentistry", "Mechanical"). The `rarityWeight`
parameter controls IDF influence (default 1.5).

### Transition Categories

| Category | Overlap | Zone Delta | Meaning |
|----------|---------|------------|---------|
| Ready Now | ≥55% | ≤0 | Can transition with existing skills |
| Trainable | 30-54% | ≤1 | Achievable with short-term training |
| Long-Term Reskill | 10-29% | any | Requires significant retraining |

### Skill Gap Analysis
Missing skills are classified by IDF rarity:
- **Critical** (IDF > 2.5): Specialized skills that are essential
- **Important** (IDF > 1.5): Moderately specialized
- **Nice-to-have** (IDF ≤ 1.5): Common/generic skills

Training time estimates: `months = IDF × 1.5 + max(0, zoneDelta) × 3`

## API

The API (`skillsprout-api.ts`) supports stateful, iterative sessions:

### Actions

| Action | Purpose |
|--------|---------|
| `search` | New or refined trajectory search |
| `more` | Paginate (excludes previously seen codes) |
| `filter` | Filter current results by category |
| `add_skills` | Add additional skills and re-run |
| `list_occupations` | Return full occupation catalog |
| `reset` | Clear session state |

### Example Session
```typescript
import { callApi } from "./lib/skillsprout-api";

// Turn 1: Initial search
const r1 = callApi({ action: "search", occupation: "Registered Nurses" });
// → { readyNow: [...], trainable: [...], longTermReskill: [...] }

// Turn 2: Filter to trainable only
const r2 = callApi({
  action: "filter",
  sessionId: r1.sessionId,
  categoryFilter: "trainable"
});

// Turn 3: Add skills and re-run
const r3 = callApi({
  action: "add_skills",
  sessionId: r1.sessionId,
  additionalSkills: ["computers and electronics", "mathematics"]
});

// Turn 4: Get more results (pagination)
const r4 = callApi({
  action: "more",
  sessionId: r1.sessionId
});
```

## Test Suite

55 test cases organized by theme:

| Theme | Count | What it tests |
|-------|-------|--------------|
| AI-Adjacent Upskilling | 8 | Tech skill corridors (BI → Data Scientist) |
| Cross-Domain Pivot | 7 | Cross-industry transitions (Nurse → Health Manager) |
| Declining-Role Escape | 5 | Automation-threatened roles finding paths out |
| Trades-to-Tech | 6 | Blue-collar → technical transitions |
| Long-Term Reskill | 8 | Zone 1-2 → Zone 4-5 ambitious reskills |
| Iterative Refinement | 5 | Multi-turn API sessions, pagination |
| Edge Cases | 7 | Error handling, partial matching, code search |
| Anthropic Paper Scenarios | 8 | Scenarios from Anthropic's AI economic impact research |
| Healthcare Transitions | 4 | Healthcare occupation ladders |
| Full-Dataset Coverage | 8 | Diverse occupations (farmers, pilots, clergy, etc.) |

Run tests in-browser via the "Test Suite" panel on the `/skillsprout/` page.

## References

- **O*NET OnLine**: https://www.onetonline.org/
- **O*NET Database 28.3**: https://www.onetcenter.org/database.html
- **Anthropic (2025)**: "The Macroeconomic Impact of Artificial Intelligence"
  — uses O*NET task/skill data to model AI-driven labor transitions
  https://www.anthropic.com/research/the-macroeconomic-impact-of-artificial-intelligence
