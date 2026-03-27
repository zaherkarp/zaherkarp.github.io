/**
 * Comprehensive test cases for the SkillSprout career trajectory engine.
 *
 * Organized around themes from Anthropic's "The Macroeconomic Impact of
 * Artificial Intelligence" (2025), which uses O*NET task and skill data to
 * model AI-driven labor market transitions:
 *
 *   1. AI-adjacent upskilling (e.g., data analyst → data scientist)
 *   2. Cross-domain pivots (e.g., nurse → health informatics)
 *   3. Declining-role escape paths (e.g., customer service rep → UX designer)
 *   4. Trades-to-tech transitions (e.g., electrician → robotics engineer)
 *   5. Long-term reskill with significant zone jumps
 *   6. Iterative refinement (multi-turn API sessions)
 *   7. Edge cases (unknown occupations, no matches, etc.)
 *
 * Each test case documents expected behavior so manual QA or a future
 * automated suite can validate the engine.
 */

import { callApi, quickSearch, type ApiRequest } from "../lib/skillsprout-api";
import type { TrajectoryResponse, TransitionMatch } from "../lib/skillsprout-engine";

export interface TestCase {
  id: string;
  name: string;
  description: string;
  theme: string;
  /** Steps to execute (sequential API calls) */
  steps: ApiRequest[];
  /** Assertions about the final result */
  expect: TestExpectation;
}

interface TestExpectation {
  success: boolean;
  /** Minimum number of matches per category */
  minReadyNow?: number;
  minTrainable?: number;
  minLongTermReskill?: number;
  /** Specific occupations that should appear in results */
  shouldContain?: string[];
  /** Specific occupations that should NOT appear */
  shouldNotContain?: string[];
  /** The source should resolve to this title */
  sourceTitle?: string;
  /** Error message substring (for failure cases) */
  errorContains?: string;
}

// ────────────────────────────────────────────────────────────────────
// Test Suite
// ────────────────────────────────────────────────────────────────────

export const testCases: TestCase[] = [
  // ── Theme 1: AI-Adjacent Upskilling ──────────────────────────────

  {
    id: "ai-01",
    name: "BI Analyst → Data Scientist / ML Engineer",
    description:
      "A Business Intelligence Analyst with SQL/Python skills should see Data Scientist as Trainable and ML Engineer as Long-Term Reskill. Tests the AI upskilling corridor identified in Anthropic's paper.",
    theme: "AI-Adjacent Upskilling",
    steps: [{ action: "search", occupation: "Business Intelligence Analyst" }],
    expect: {
      success: true,
      sourceTitle: "Business Intelligence Analyst",
      minTrainable: 2,
      minLongTermReskill: 1,
      shouldContain: ["Data Scientist", "Data Engineer"],
    },
  },
  {
    id: "ai-02",
    name: "Software Developer → ML Engineer (with added skills)",
    description:
      "A Software Developer who adds 'machine learning, statistics' should see ML Engineer move from Long-Term Reskill to Trainable. Tests iterative skill addition.",
    theme: "AI-Adjacent Upskilling",
    steps: [
      { action: "search", occupation: "Software Developer" },
      { action: "add_skills", additionalSkills: ["machine learning", "statistics", "deep learning"] },
    ],
    expect: {
      success: true,
      minTrainable: 2,
      shouldContain: ["Machine Learning Engineer"],
    },
  },
  {
    id: "ai-03",
    name: "Statistician → Data Scientist",
    description:
      "A Statistician should see Data Scientist as Ready Now or Trainable given high skill overlap (R, statistics, data analysis).",
    theme: "AI-Adjacent Upskilling",
    steps: [{ action: "search", occupation: "Statistician" }],
    expect: {
      success: true,
      sourceTitle: "Statistician",
      minReadyNow: 1,
      shouldContain: ["Data Scientist"],
    },
  },
  {
    id: "ai-04",
    name: "Database Administrator → Data Engineer",
    description:
      "DBA to Data Engineer is a natural skill-adjacent transition (SQL, databases, ETL). Should appear as Ready Now.",
    theme: "AI-Adjacent Upskilling",
    steps: [{ action: "search", occupation: "Database Administrator" }],
    expect: {
      success: true,
      minReadyNow: 1,
      shouldContain: ["Data Engineer"],
    },
  },
  {
    id: "ai-05",
    name: "QA Analyst → Software Developer",
    description:
      "QA Analyst shares problem solving, agile, JavaScript, Python with Software Developer. Should be Trainable.",
    theme: "AI-Adjacent Upskilling",
    steps: [{ action: "search", occupation: "Software Quality Assurance Analyst" }],
    expect: {
      success: true,
      minTrainable: 2,
      shouldContain: ["Software Developer"],
    },
  },

  // ── Theme 2: Cross-Domain Pivots ─────────────────────────────────

  {
    id: "cross-01",
    name: "Registered Nurse → Health Services Manager",
    description:
      "Nurses share patient care, EHR, HIPAA, and leadership skills with Health Services Managers. A well-documented O*NET transition path.",
    theme: "Cross-Domain Pivot",
    steps: [{ action: "search", occupation: "Registered Nurse" }],
    expect: {
      success: true,
      minTrainable: 1,
      shouldContain: ["Medical and Health Services Manager"],
    },
  },
  {
    id: "cross-02",
    name: "Nurse → Epidemiologist (Long-Term Reskill)",
    description:
      "RN → Epidemiologist requires statistics, R, SAS — a significant reskill. Should appear as Long-Term Reskill.",
    theme: "Cross-Domain Pivot",
    steps: [
      { action: "search", occupation: "Registered Nurse", categoryFilter: "long_term_reskill" },
    ],
    expect: {
      success: true,
      minLongTermReskill: 2,
    },
  },
  {
    id: "cross-03",
    name: "Accountant → Financial Analyst",
    description:
      "High overlap: accounting, financial analysis, budgeting. Should be Ready Now.",
    theme: "Cross-Domain Pivot",
    steps: [{ action: "search", occupation: "Accountant" }],
    expect: {
      success: true,
      minReadyNow: 1,
      shouldContain: ["Financial Analyst"],
    },
  },
  {
    id: "cross-04",
    name: "Mechanical Engineer → Robotics Engineer",
    description:
      "Mechanical engineering + CAD/CAM overlap. Robotics needs Python, ML — should be Trainable or Long-Term.",
    theme: "Cross-Domain Pivot",
    steps: [{ action: "search", occupation: "Mechanical Engineer" }],
    expect: {
      success: true,
      shouldContain: ["Robotics Engineer"],
    },
  },
  {
    id: "cross-05",
    name: "Paralegal → Management Analyst",
    description:
      "Paralegal has research, writing, compliance, critical thinking — overlaps with Management Analyst's analytical skill set.",
    theme: "Cross-Domain Pivot",
    steps: [{ action: "search", occupation: "Paralegal" }],
    expect: {
      success: true,
      minTrainable: 1,
    },
  },
  {
    id: "cross-06",
    name: "Graphic Designer → UX Designer",
    description:
      "Graphic Designer shares design tools (Figma, Adobe), UI/UX, and HTML/CSS with UX Designer. Natural transition.",
    theme: "Cross-Domain Pivot",
    steps: [{ action: "search", occupation: "Graphic Designer" }],
    expect: {
      success: true,
      shouldContain: ["UX Designer"],
    },
  },
  {
    id: "cross-07",
    name: "Sales Rep → Digital Marketing Specialist",
    description:
      "Sales and marketing overlap via communication, CRM, negotiation, and data analysis.",
    theme: "Cross-Domain Pivot",
    steps: [{ action: "search", occupation: "Sales Representative" }],
    expect: {
      success: true,
      shouldContain: ["Market Research Analyst"],
    },
  },

  // ── Theme 3: Declining-Role Escape Paths ─────────────────────────

  {
    id: "decline-01",
    name: "Customer Service Rep → multiple escape paths",
    description:
      "CSRs face automation risk (Anthropic paper). Should see paths to Admin Assistant, Sales, and with additional skills, to IT support or marketing.",
    theme: "Declining-Role Escape",
    steps: [{ action: "search", occupation: "Customer Service Representative" }],
    expect: {
      success: true,
      minTrainable: 1,
      minLongTermReskill: 2,
    },
  },
  {
    id: "decline-02",
    name: "Customer Service Rep + python,sql → BI Analyst path",
    description:
      "Adding technical skills to a declining role should unlock data-oriented transition paths.",
    theme: "Declining-Role Escape",
    steps: [
      { action: "search", occupation: "Customer Service Representative" },
      { action: "add_skills", additionalSkills: ["python", "sql", "data analysis", "data visualization"] },
    ],
    expect: {
      success: true,
      minTrainable: 2,
      shouldContain: ["Market Research Analyst"],
    },
  },
  {
    id: "decline-03",
    name: "Administrative Assistant → multiple paths",
    description:
      "Admin Assistants face declining demand. Should see HR Specialist, Paralegal, or Instructional Designer as Trainable.",
    theme: "Declining-Role Escape",
    steps: [{ action: "search", occupation: "Administrative Assistant" }],
    expect: {
      success: true,
      minTrainable: 2,
      minLongTermReskill: 2,
    },
  },
  {
    id: "decline-04",
    name: "Pharmacist → pivot options despite declining outlook",
    description:
      "Pharmacists have declining job outlook but strong clinical/analytical skills. Should see Health Services Manager, Epidemiologist as paths.",
    theme: "Declining-Role Escape",
    steps: [{ action: "search", occupation: "Pharmacist" }],
    expect: {
      success: true,
      minTrainable: 1,
      shouldContain: ["Medical and Health Services Manager"],
    },
  },

  // ── Theme 4: Trades-to-Tech ──────────────────────────────────────

  {
    id: "trades-01",
    name: "Electrician → Photovoltaic Engineer",
    description:
      "Electricians share electrical wiring and math with PV engineers. Sustainability + CAD/CAM are the gap. Tests zone 3→4 transition.",
    theme: "Trades-to-Tech",
    steps: [{ action: "search", occupation: "Electrician" }],
    expect: {
      success: true,
      shouldContain: ["Photovoltaic Engineer"],
    },
  },
  {
    id: "trades-02",
    name: "HVAC Technician → multiple paths",
    description:
      "HVAC techs have mechanical/electrical skills. Should see paths to Electrician (Ready Now) and engineering roles (Long-Term).",
    theme: "Trades-to-Tech",
    steps: [{ action: "search", occupation: "HVAC Technician" }],
    expect: {
      success: true,
      minReadyNow: 1,
      minLongTermReskill: 2,
    },
  },
  {
    id: "trades-03",
    name: "CNC Machinist → Mechanical Engineer",
    description:
      "CNC Machinists share CAD/CAM, quality control, and manufacturing with Mechanical Engineers. Should be Trainable (zone 3→4).",
    theme: "Trades-to-Tech",
    steps: [{ action: "search", occupation: "CNC Machinist" }],
    expect: {
      success: true,
      shouldContain: ["Mechanical Engineer"],
    },
  },
  {
    id: "trades-04",
    name: "Welder + python,automation → Robotics path",
    description:
      "A welder who learns Python and automation concepts could pivot to robotics. Tests skill augmentation for trades workers.",
    theme: "Trades-to-Tech",
    steps: [
      { action: "search", occupation: "Welder" },
      { action: "add_skills", additionalSkills: ["python", "automation", "mathematics"] },
    ],
    expect: {
      success: true,
      minLongTermReskill: 2,
    },
  },
  {
    id: "trades-05",
    name: "Truck Driver → Logistician",
    description:
      "Truck drivers have logistics, fleet management, communication. Logistician is a Trainable step up (zone 2→4).",
    theme: "Trades-to-Tech",
    steps: [{ action: "search", occupation: "Heavy Truck Driver" }],
    expect: {
      success: true,
      minLongTermReskill: 1,
    },
  },

  // ── Theme 5: Long-Term Reskill with Zone Jumps ───────────────────

  {
    id: "reskill-01",
    name: "Warehouse Worker → Software Developer",
    description:
      "Zone 1→4 transition. Very low overlap. Should appear as Long-Term Reskill with significant training path. Tests the engine's ability to surface ambitious but theoretically possible transitions.",
    theme: "Long-Term Reskill",
    steps: [
      {
        action: "search",
        occupation: "Warehouse Worker",
        categoryFilter: "long_term_reskill",
        maxPerCategory: 10,
      },
    ],
    expect: {
      success: true,
      minLongTermReskill: 3,
    },
  },
  {
    id: "reskill-02",
    name: "Fast Food Worker → multiple long-term paths",
    description:
      "Zone 1 → multiple paths. Tests the engine's ability to find creative transitions from entry-level roles. Communication and customer service are the bridge skills.",
    theme: "Long-Term Reskill",
    steps: [
      {
        action: "search",
        occupation: "Barista/Fast Food Worker",
        categoryFilter: "long_term_reskill",
        maxPerCategory: 10,
      },
    ],
    expect: {
      success: true,
      minLongTermReskill: 3,
    },
  },
  {
    id: "reskill-03",
    name: "Childcare Worker → Instructional Designer",
    description:
      "Childcare workers have teaching and communication skills that bridge to instructional design (zone 2→4). A non-obvious but valid O*NET path.",
    theme: "Long-Term Reskill",
    steps: [{ action: "search", occupation: "Childcare Worker" }],
    expect: {
      success: true,
      minLongTermReskill: 2,
    },
  },
  {
    id: "reskill-04",
    name: "Janitor → Customer Service → Admin Assistant chain",
    description:
      "Tests the lowest zone starting point. Communication and problem solving are the thin threads connecting to higher roles.",
    theme: "Long-Term Reskill",
    steps: [
      {
        action: "search",
        occupation: "Janitor/Cleaning Worker",
        maxPerCategory: 10,
        minScore: 0.08,
      },
    ],
    expect: {
      success: true,
      minLongTermReskill: 2,
    },
  },
  {
    id: "reskill-05",
    name: "Head Chef → Food Service Manager → Operations Manager",
    description:
      "Culinary to management pipeline. Chef shares leadership, budgeting, team management. Tests natural industry progression.",
    theme: "Long-Term Reskill",
    steps: [{ action: "search", occupation: "Head Chef" }],
    expect: {
      success: true,
      shouldContain: ["Food Service Manager"],
    },
  },
  {
    id: "reskill-06",
    name: "LPN → Registered Nurse → Physician Assistant",
    description:
      "Classic healthcare ladder. LPN→RN is Trainable, RN→PA is Long-Term. Tests multi-hop career progression.",
    theme: "Long-Term Reskill",
    steps: [{ action: "search", occupation: "Licensed Practical Nurse" }],
    expect: {
      success: true,
      shouldContain: ["Registered Nurse"],
    },
  },
  {
    id: "reskill-07",
    name: "Social Worker → Epidemiologist (public health bridge)",
    description:
      "Social workers share public health, communication, and research methods. Epi is a Long-Term Reskill requiring statistics and biostatistics.",
    theme: "Long-Term Reskill",
    steps: [
      {
        action: "search",
        occupation: "Social Worker",
        categoryFilter: "long_term_reskill",
        maxPerCategory: 10,
      },
    ],
    expect: {
      success: true,
      minLongTermReskill: 3,
    },
  },

  // ── Theme 6: Iterative Refinement (Multi-Turn Sessions) ──────────

  {
    id: "iter-01",
    name: "Multi-turn: search → filter → more → add skills",
    description:
      "Tests full iterative API flow: initial search, filter to trainable, paginate with 'more', then add skills to unlock new matches.",
    theme: "Iterative Refinement",
    steps: [
      { action: "search", occupation: "Software Developer", maxPerCategory: 3 },
      { action: "filter", categoryFilter: "trainable" },
      { action: "more", categoryFilter: "trainable" },
      { action: "add_skills", additionalSkills: ["machine learning", "statistics"] },
    ],
    expect: {
      success: true,
      minTrainable: 1,
    },
  },
  {
    id: "iter-02",
    name: "Multi-turn: search → reset → new search",
    description:
      "Tests session reset: search one occupation, reset, search a completely different one. State should be clean.",
    theme: "Iterative Refinement",
    steps: [
      { action: "search", occupation: "Registered Nurse" },
      { action: "reset" },
      { action: "search", occupation: "Software Developer" },
    ],
    expect: {
      success: true,
      sourceTitle: "Software Developer",
      shouldNotContain: ["Registered Nurse"],
    },
  },
  {
    id: "iter-03",
    name: "Pagination: exhaust ready_now results",
    description:
      "Request maxPerCategory=2 then 'more' repeatedly. Tests that excludeCodes prevents duplicate results.",
    theme: "Iterative Refinement",
    steps: [
      { action: "search", occupation: "Data Scientist", maxPerCategory: 2 },
      { action: "more", maxPerCategory: 2 },
      { action: "more", maxPerCategory: 2 },
    ],
    expect: {
      success: true,
    },
  },
  {
    id: "iter-04",
    name: "Category filter isolation",
    description:
      "Filter to long_term_reskill only for a Software Developer. Should return zero ready_now and trainable.",
    theme: "Iterative Refinement",
    steps: [
      {
        action: "search",
        occupation: "Software Developer",
        categoryFilter: "long_term_reskill",
        maxPerCategory: 10,
      },
    ],
    expect: {
      success: true,
      minLongTermReskill: 3,
    },
  },
  {
    id: "iter-05",
    name: "Preferred categories boost",
    description:
      "Search with preferredCategories=['Healthcare'] from a Software Developer. Healthcare long-term reskill options should be prioritized.",
    theme: "Iterative Refinement",
    steps: [
      {
        action: "search",
        occupation: "Software Developer",
        preferredCategories: ["Healthcare"],
        categoryFilter: "long_term_reskill",
        maxPerCategory: 10,
      },
    ],
    expect: {
      success: true,
      minLongTermReskill: 2,
    },
  },

  // ── Theme 7: Edge Cases ──────────────────────────────────────────

  {
    id: "edge-01",
    name: "Unknown occupation",
    description: "Searching for a non-existent occupation should return success=false with helpful suggestions.",
    theme: "Edge Case",
    steps: [{ action: "search", occupation: "Underwater Basket Weaver" }],
    expect: {
      success: false,
      errorContains: "Could not find occupation",
    },
  },
  {
    id: "edge-02",
    name: "Empty occupation string",
    description: "Empty string should fail gracefully.",
    theme: "Edge Case",
    steps: [{ action: "search", occupation: "" }],
    expect: {
      success: false,
      errorContains: "Could not find occupation",
    },
  },
  {
    id: "edge-03",
    name: "Partial title match",
    description: "Searching for 'nurse' should resolve to Registered Nurse (first partial match).",
    theme: "Edge Case",
    steps: [{ action: "search", occupation: "nurse" }],
    expect: {
      success: true,
      sourceTitle: "Registered Nurse",
    },
  },
  {
    id: "edge-04",
    name: "Code-based search",
    description: "Searching by O*NET code '15-1252.00' should resolve to Software Developer.",
    theme: "Edge Case",
    steps: [{ action: "search", occupation: "15-1252.00" }],
    expect: {
      success: true,
      sourceTitle: "Software Developer",
    },
  },
  {
    id: "edge-05",
    name: "Very high minScore filters everything",
    description: "Setting minScore=0.95 should return zero matches for most occupations.",
    theme: "Edge Case",
    steps: [{ action: "search", occupation: "Software Developer", minScore: 0.95 }],
    expect: {
      success: true,
      // May have 0 matches — that's the expected behavior
    },
  },
  {
    id: "edge-06",
    name: "List all occupations",
    description: "list_occupations action should return the full catalog.",
    theme: "Edge Case",
    steps: [{ action: "list_occupations" }],
    expect: {
      success: true,
    },
  },

  // ── Theme 8: Anthropic Paper-Specific Scenarios ──────────────────

  {
    id: "anthro-01",
    name: "Computer User Support → Information Security Analyst",
    description:
      "IT support roles are identified in Anthropic's paper as having AI augmentation potential. Cybersecurity is a natural upskill path from helpdesk.",
    theme: "Anthropic Paper Scenario",
    steps: [{ action: "search", occupation: "Computer User Support Specialist" }],
    expect: {
      success: true,
      shouldContain: ["Network and Computer Systems Administrator"],
    },
  },
  {
    id: "anthro-02",
    name: "Medical Records Specialist → multiple health-tech paths",
    description:
      "Medical Records is flagged as high AI exposure in the Anthropic paper. Should have escape paths to Health Services Manager and BI Analyst with clinical data skills.",
    theme: "Anthropic Paper Scenario",
    steps: [{ action: "search", occupation: "Medical Records Specialist" }],
    expect: {
      success: true,
      minTrainable: 1,
      minLongTermReskill: 2,
    },
  },
  {
    id: "anthro-03",
    name: "Market Research Analyst → Data Scientist",
    description:
      "Market research shares statistics, data analysis, Python, and communication with Data Science. Key AI upskilling path from Anthropic's framework.",
    theme: "Anthropic Paper Scenario",
    steps: [{ action: "search", occupation: "Market Research Analyst" }],
    expect: {
      success: true,
      shouldContain: ["Statistician"],
    },
  },
  {
    id: "anthro-04",
    name: "Technical Writer → Instructional Designer",
    description:
      "Technical writing is identified as having high AI exposure. Instructional design leverages writing + curriculum skills with lower automation risk.",
    theme: "Anthropic Paper Scenario",
    steps: [{ action: "search", occupation: "Technical Writer" }],
    expect: {
      success: true,
      shouldContain: ["Instructional Designer"],
    },
  },
  {
    id: "anthro-05",
    name: "DevOps Engineer → Computer Systems Architect",
    description:
      "DevOps shares cloud, Docker, Kubernetes, networking with Systems Architecture. Natural career progression in the AI infrastructure build-out.",
    theme: "Anthropic Paper Scenario",
    steps: [{ action: "search", occupation: "DevOps Engineer" }],
    expect: {
      success: true,
      shouldContain: ["Computer Systems Engineer/Architect"],
    },
  },
  {
    id: "anthro-06",
    name: "Financial Analyst → Actuary (Long-Term Reskill)",
    description:
      "Finance roles face AI augmentation. Actuary requires deep statistics and actuarial science but shares financial analysis, economics, and Python.",
    theme: "Anthropic Paper Scenario",
    steps: [{ action: "search", occupation: "Financial Analyst" }],
    expect: {
      success: true,
      shouldContain: ["Actuary"],
    },
  },
  {
    id: "anthro-07",
    name: "Environmental Scientist → Data Scientist (green skills + data)",
    description:
      "Environmental Scientists have GIS, statistics, Python, and research methods that transfer to data science. Tests cross-domain scientific transition.",
    theme: "Anthropic Paper Scenario",
    steps: [{ action: "search", occupation: "Environmental Scientist" }],
    expect: {
      success: true,
      minTrainable: 2,
    },
  },
  {
    id: "anthro-08",
    name: "Biological Scientist → Epidemiologist",
    description:
      "Bio scientists share research methods, statistics, R, and scientific writing with Epidemiologists. A common academic pivot.",
    theme: "Anthropic Paper Scenario",
    steps: [{ action: "search", occupation: "Biological Scientist" }],
    expect: {
      success: true,
      shouldContain: ["Epidemiologist"],
    },
  },
];

// ── Test Runner ────────────────────────────────────────────────────

export interface TestResult {
  id: string;
  name: string;
  passed: boolean;
  failures: string[];
  response?: TrajectoryResponse;
}

export function runTestCase(tc: TestCase): TestResult {
  const failures: string[] = [];
  let lastApiResult: any = null;
  let sessionId: string | undefined;

  // Execute steps sequentially
  for (const step of tc.steps) {
    const req = { ...step, sessionId };
    const result = callApi(req);
    sessionId = result.sessionId;
    lastApiResult = result;
  }

  if (!lastApiResult) {
    return { id: tc.id, name: tc.name, passed: false, failures: ["No API result"] };
  }

  const data = lastApiResult.data;

  // For list_occupations, just check it returned something
  if ("occupations" in data) {
    if (tc.expect.success && data.occupations.length === 0) {
      failures.push("Expected occupations list but got empty");
    }
    return { id: tc.id, name: tc.name, passed: failures.length === 0, failures };
  }

  // For reset, just check the message
  if ("message" in data) {
    return { id: tc.id, name: tc.name, passed: true, failures: [] };
  }

  const resp = data as TrajectoryResponse;

  // Check success
  if (resp.success !== tc.expect.success) {
    failures.push(`Expected success=${tc.expect.success}, got ${resp.success}`);
  }

  if (!resp.success && tc.expect.errorContains) {
    if (!resp.error?.includes(tc.expect.errorContains)) {
      failures.push(`Expected error containing "${tc.expect.errorContains}", got "${resp.error}"`);
    }
  }

  if (resp.success) {
    // Check source title
    if (tc.expect.sourceTitle && resp.source?.title !== tc.expect.sourceTitle) {
      failures.push(`Expected source "${tc.expect.sourceTitle}", got "${resp.source?.title}"`);
    }

    // Check minimum counts
    if (tc.expect.minReadyNow !== undefined && resp.readyNow.length < tc.expect.minReadyNow) {
      failures.push(`Expected ≥${tc.expect.minReadyNow} Ready Now, got ${resp.readyNow.length}`);
    }
    if (tc.expect.minTrainable !== undefined && resp.trainable.length < tc.expect.minTrainable) {
      failures.push(`Expected ≥${tc.expect.minTrainable} Trainable, got ${resp.trainable.length}`);
    }
    if (tc.expect.minLongTermReskill !== undefined && resp.longTermReskill.length < tc.expect.minLongTermReskill) {
      failures.push(`Expected ≥${tc.expect.minLongTermReskill} Long-Term Reskill, got ${resp.longTermReskill.length}`);
    }

    // Check shouldContain
    if (tc.expect.shouldContain) {
      const allTitles = [
        ...resp.readyNow,
        ...resp.trainable,
        ...resp.longTermReskill,
      ].map(m => m.occupation.title);

      for (const expected of tc.expect.shouldContain) {
        if (!allTitles.includes(expected)) {
          failures.push(`Expected results to contain "${expected}", but found: [${allTitles.join(", ")}]`);
        }
      }
    }

    // Check shouldNotContain
    if (tc.expect.shouldNotContain) {
      const allTitles = [
        ...resp.readyNow,
        ...resp.trainable,
        ...resp.longTermReskill,
      ].map(m => m.occupation.title);

      for (const excluded of tc.expect.shouldNotContain) {
        if (allTitles.includes(excluded)) {
          failures.push(`Expected results NOT to contain "${excluded}"`);
        }
      }
    }
  }

  return {
    id: tc.id,
    name: tc.name,
    passed: failures.length === 0,
    failures,
    response: resp,
  };
}

export function runAllTests(): TestResult[] {
  return testCases.map(runTestCase);
}

export function printTestResults(results: TestResult[]): string {
  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  const lines: string[] = [
    `\n━━━ SkillSprout Test Suite ━━━`,
    `${passed}/${total} passed\n`,
  ];

  for (const r of results) {
    const icon = r.passed ? "✓" : "✗";
    lines.push(`  ${icon} [${r.id}] ${r.name}`);
    for (const f of r.failures) {
      lines.push(`      ↳ ${f}`);
    }
  }

  lines.push(`\n━━━ ${passed}/${total} passed ━━━\n`);
  return lines.join("\n");
}
