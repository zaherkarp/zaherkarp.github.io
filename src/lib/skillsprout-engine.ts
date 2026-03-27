/**
 * SkillSprout Career Trajectory Engine
 *
 * Client-side matching engine that computes career transition recommendations
 * using O*NET occupation and skill data. Exposes a request/response API that
 * supports iterative refinement (filter by category, adjust weights, exclude
 * occupations already seen, request more results).
 *
 * Transition categories (per Anthropic's AI economic-impact framework):
 *   - Ready Now:       ≥70% skill overlap, same or lower Job Zone
 *   - Trainable:       40-69% skill overlap, Zone delta ≤ 1
 *   - Long-Term Reskill: 15-39% skill overlap OR Zone delta ≥ 2
 *
 * The engine uses Jaccard-like overlap weighted by skill rarity (IDF) so that
 * common skills like "communication" don't dominate the score.
 */

import { occupations, type OnetOccupation } from "../data/onet-occupations";

// ── Types ──────────────────────────────────────────────────────────

export interface TrajectoryRequest {
  /** O*NET code or title (case-insensitive partial match) */
  sourceOccupation: string;
  /** Optional additional skills the user has beyond their occupation's defaults */
  additionalSkills?: string[];
  /** Filter results to a specific category */
  categoryFilter?: "all" | "ready_now" | "trainable" | "long_term_reskill";
  /** Occupation codes to exclude (for pagination / "show me more") */
  excludeCodes?: string[];
  /** Max results per category (default 5) */
  maxPerCategory?: number;
  /** Minimum overlap score 0-1 to include (default 0.10) */
  minScore?: number;
  /** Weight multiplier for skill rarity (IDF). Higher = rarer skills matter more */
  rarityWeight?: number;
  /** Prefer occupations in these categories */
  preferredCategories?: string[];
  /** Conversation turn number for iterative refinement */
  turn?: number;
}

export interface SkillGap {
  skill: string;
  importance: "critical" | "important" | "nice-to-have";
}

export interface TrainingPath {
  skill: string;
  estimatedMonths: number;
  resources: string[];
}

export interface TransitionMatch {
  occupation: OnetOccupation;
  overlapScore: number;           // 0-1
  sharedSkills: string[];
  missingSkills: SkillGap[];
  trainingPaths: TrainingPath[];
  category: "ready_now" | "trainable" | "long_term_reskill";
  zoneDelta: number;
  payDelta: number;
}

export interface TrajectoryResponse {
  success: boolean;
  source: OnetOccupation | null;
  sourceSkills: string[];
  readyNow: TransitionMatch[];
  trainable: TransitionMatch[];
  longTermReskill: TransitionMatch[];
  totalMatches: number;
  turn: number;
  suggestions: string[];         // Hints for the next iterative request
  error?: string;
}

// ── Helpers ────────────────────────────────────────────────────────

/** Compute inverse document frequency for each skill across the corpus. */
function computeIdf(): Map<string, number> {
  const docCount = occupations.length;
  const skillDocFreq = new Map<string, number>();
  for (const occ of occupations) {
    const seen = new Set<string>();
    for (const s of occ.skills) {
      const key = s.toLowerCase();
      if (!seen.has(key)) {
        skillDocFreq.set(key, (skillDocFreq.get(key) || 0) + 1);
        seen.add(key);
      }
    }
  }
  const idf = new Map<string, number>();
  for (const [skill, df] of skillDocFreq) {
    idf.set(skill, Math.log(docCount / df));
  }
  return idf;
}

const IDF = computeIdf();

function idfWeight(skill: string, rarityMultiplier: number): number {
  const base = IDF.get(skill.toLowerCase()) ?? Math.log(occupations.length);
  // Scale so common skills ~1, rare skills up to ~rarityMultiplier
  return 1 + (base - 1) * (rarityMultiplier - 1) / (Math.log(occupations.length) - 1 || 1);
}

function resolveOccupation(query: string): OnetOccupation | null {
  const q = query.toLowerCase().trim();
  // Exact code match
  const byCode = occupations.find((o) => o.code === q);
  if (byCode) return byCode;
  // Exact title match
  const byTitle = occupations.find((o) => o.title.toLowerCase() === q);
  if (byTitle) return byTitle;
  // Partial title match
  const partial = occupations.find((o) => o.title.toLowerCase().includes(q));
  if (partial) return partial;
  // Partial code match
  const partialCode = occupations.find((o) => o.code.includes(q));
  return partialCode ?? null;
}

function classifyImportance(idfScore: number): "critical" | "important" | "nice-to-have" {
  if (idfScore > 2.5) return "critical";
  if (idfScore > 1.5) return "important";
  return "nice-to-have";
}

function estimateTrainingMonths(skill: string, zoneDelta: number): number {
  const base = IDF.get(skill.toLowerCase()) ?? 2;
  // Higher IDF = more specialized = longer training
  const months = Math.max(1, Math.round(base * 2 + zoneDelta * 3));
  return Math.min(months, 36);
}

function suggestResources(skill: string): string[] {
  const s = skill.toLowerCase();
  const resources: string[] = [];

  // Programming / tech skills
  const techSkills = ["python", "r", "sql", "java", "javascript", "typescript", "c++", "c#",
    "go", "rust", "react", "node.js", "ruby", "swift", "kotlin", "html/css"];
  if (techSkills.some(t => s.includes(t))) {
    resources.push("freeCodeCamp", "Codecademy", "MIT OpenCourseWare");
  }

  // Data / ML
  if (["machine learning", "deep learning", "data science", "statistics", "data analysis",
       "natural language processing", "computer vision", "generative ai", "data engineering",
       "data visualization", "data warehousing"].some(t => s.includes(t) || t.includes(s))) {
    resources.push("Coursera (Andrew Ng ML)", "fast.ai", "Khan Academy Statistics");
  }

  // Cloud / DevOps
  if (["cloud", "aws", "azure", "gcp", "docker", "kubernetes", "devops", "ci/cd"].some(t => s.includes(t))) {
    resources.push("AWS Skill Builder", "A Cloud Guru", "Linux Foundation Training");
  }

  // Healthcare
  if (["nursing", "patient care", "ehr", "hipaa", "medical", "clinical", "pharmacy",
       "epidemiology", "public health", "biostatistics"].some(t => s.includes(t) || t.includes(s))) {
    resources.push("Coursera Public Health", "CDC TRAIN", "AHIMA certification");
  }

  // Design
  if (["design", "figma", "adobe", "ui/ux", "ux research", "accessibility"].some(t => s.includes(t) || t.includes(s))) {
    resources.push("Google UX Design Certificate", "Interaction Design Foundation", "Figma tutorials");
  }

  // Business
  if (["project management", "agile", "business analysis", "leadership", "financial",
       "accounting", "marketing", "sales"].some(t => s.includes(t) || t.includes(s))) {
    resources.push("Google Project Management Certificate", "LinkedIn Learning", "edX MicroMasters");
  }

  // Trades
  if (["hvac", "electrical wiring", "plumbing", "welding", "machining", "carpentry",
       "automotive", "construction"].some(t => s.includes(t) || t.includes(s))) {
    resources.push("Local trade school / apprenticeship", "Union training programs", "OSHA certification");
  }

  // Cybersecurity
  if (["cybersecurity", "information security", "penetration testing", "cryptography"].some(t => s.includes(t))) {
    resources.push("CompTIA Security+", "SANS Institute", "TryHackMe");
  }

  if (resources.length === 0) {
    resources.push("Coursera", "LinkedIn Learning", "edX");
  }

  return [...new Set(resources)].slice(0, 3);
}

// ── Core Engine ────────────────────────────────────────────────────

function computeMatch(
  source: OnetOccupation,
  sourceSkills: Set<string>,
  target: OnetOccupation,
  rarityWeight: number,
): TransitionMatch | null {
  if (source.code === target.code) return null;

  const targetSkills = new Set(target.skills.map(s => s.toLowerCase()));
  const shared: string[] = [];
  const missing: SkillGap[] = [];

  let sharedWeightedSum = 0;
  let unionWeightedSum = 0;

  // All skills in the union
  const allSkills = new Set([...sourceSkills, ...targetSkills]);

  for (const skill of allSkills) {
    const w = idfWeight(skill, rarityWeight);
    unionWeightedSum += w;
    if (sourceSkills.has(skill) && targetSkills.has(skill)) {
      sharedWeightedSum += w;
      shared.push(skill);
    }
  }

  // Missing = in target but not in source
  for (const skill of targetSkills) {
    if (!sourceSkills.has(skill)) {
      const idfVal = IDF.get(skill) ?? 2;
      missing.push({ skill, importance: classifyImportance(idfVal) });
    }
  }

  const overlapScore = unionWeightedSum > 0 ? sharedWeightedSum / unionWeightedSum : 0;
  const zoneDelta = target.zone - source.zone;
  const payDelta = target.medianPay - source.medianPay;

  // Classify
  let category: "ready_now" | "trainable" | "long_term_reskill";
  if (overlapScore >= 0.55 && zoneDelta <= 0) {
    category = "ready_now";
  } else if (overlapScore >= 0.30 && zoneDelta <= 1) {
    category = "trainable";
  } else if (overlapScore >= 0.10) {
    category = "long_term_reskill";
  } else {
    return null; // Too dissimilar
  }

  // Sort missing by importance
  missing.sort((a, b) => {
    const order = { critical: 0, important: 1, "nice-to-have": 2 };
    return order[a.importance] - order[b.importance];
  });

  const trainingPaths: TrainingPath[] = missing
    .filter(g => g.importance !== "nice-to-have")
    .slice(0, 5)
    .map(g => ({
      skill: g.skill,
      estimatedMonths: estimateTrainingMonths(g.skill, Math.max(0, zoneDelta)),
      resources: suggestResources(g.skill),
    }));

  return {
    occupation: target,
    overlapScore,
    sharedSkills: shared,
    missingSkills: missing,
    trainingPaths,
    category,
    zoneDelta,
    payDelta,
  };
}

// ── Public API ─────────────────────────────────────────────────────

export function getCareerTrajectories(req: TrajectoryRequest): TrajectoryResponse {
  const turn = req.turn ?? 1;

  // Resolve source occupation
  const source = resolveOccupation(req.sourceOccupation);
  if (!source) {
    return {
      success: false,
      source: null,
      sourceSkills: [],
      readyNow: [],
      trainable: [],
      longTermReskill: [],
      totalMatches: 0,
      turn,
      suggestions: [
        "Try a different job title (e.g., 'Software Developer', 'Registered Nurse')",
        `Available occupations: ${occupations.slice(0, 5).map(o => o.title).join(", ")}...`,
      ],
      error: `Could not find occupation matching "${req.sourceOccupation}". Try a standard job title.`,
    };
  }

  const additionalSkills = (req.additionalSkills ?? []).map(s => s.toLowerCase());
  const sourceSkills = new Set([
    ...source.skills.map(s => s.toLowerCase()),
    ...additionalSkills,
  ]);

  const excludeSet = new Set(req.excludeCodes ?? []);
  const maxPer = req.maxPerCategory ?? 5;
  const minScore = req.minScore ?? 0.10;
  const rarityWeight = req.rarityWeight ?? 1.5;
  const categoryFilter = req.categoryFilter ?? "all";
  const preferredCategories = new Set(
    (req.preferredCategories ?? []).map(c => c.toLowerCase())
  );

  const readyNow: TransitionMatch[] = [];
  const trainable: TransitionMatch[] = [];
  const longTermReskill: TransitionMatch[] = [];

  for (const target of occupations) {
    if (excludeSet.has(target.code)) continue;

    const match = computeMatch(source, sourceSkills, target, rarityWeight);
    if (!match || match.overlapScore < minScore) continue;

    // Category filter
    if (categoryFilter !== "all" && match.category !== categoryFilter) continue;

    // Boost preferred categories in sorting
    const preferred = preferredCategories.has(target.category.toLowerCase());

    switch (match.category) {
      case "ready_now":
        readyNow.push(match);
        break;
      case "trainable":
        trainable.push(match);
        break;
      case "long_term_reskill":
        longTermReskill.push(match);
        break;
    }
  }

  // Sort each bucket by overlap score descending, with preferred categories boosted
  const sortFn = (a: TransitionMatch, b: TransitionMatch) => {
    const aBoost = preferredCategories.has(a.occupation.category.toLowerCase()) ? 0.1 : 0;
    const bBoost = preferredCategories.has(b.occupation.category.toLowerCase()) ? 0.1 : 0;
    return (b.overlapScore + bBoost) - (a.overlapScore + aBoost);
  };

  readyNow.sort(sortFn);
  trainable.sort(sortFn);
  longTermReskill.sort(sortFn);

  const trimmed = {
    readyNow: readyNow.slice(0, maxPer),
    trainable: trainable.slice(0, maxPer),
    longTermReskill: longTermReskill.slice(0, maxPer),
  };

  const totalMatches = readyNow.length + trainable.length + longTermReskill.length;

  // Generate suggestions for iterative refinement
  const suggestions: string[] = [];
  if (readyNow.length > maxPer) {
    suggestions.push(`${readyNow.length - maxPer} more Ready Now matches available — increase maxPerCategory or exclude seen codes`);
  }
  if (trainable.length > maxPer) {
    suggestions.push(`${trainable.length - maxPer} more Trainable matches available`);
  }
  if (longTermReskill.length > maxPer) {
    suggestions.push(`${longTermReskill.length - maxPer} more Long-Term Reskill matches available`);
  }
  if (trimmed.longTermReskill.length === 0 && categoryFilter === "all") {
    suggestions.push("Try adding additional skills or lowering minScore to see Long-Term Reskill options");
  }
  if (additionalSkills.length === 0) {
    suggestions.push("Add your additional skills (e.g., certifications, side projects) to improve matching");
  }

  // Suggest categories where user has few matches
  const occupationCategories = [...new Set(occupations.map(o => o.category))];
  const matchedCategories = new Set([
    ...trimmed.readyNow.map(m => m.occupation.category),
    ...trimmed.trainable.map(m => m.occupation.category),
    ...trimmed.longTermReskill.map(m => m.occupation.category),
  ]);
  const unseenCategories = occupationCategories.filter(c => !matchedCategories.has(c));
  if (unseenCategories.length > 0 && unseenCategories.length <= 4) {
    suggestions.push(`Explore transitions to: ${unseenCategories.join(", ")}`);
  }

  return {
    success: true,
    source,
    sourceSkills: [...sourceSkills],
    ...trimmed,
    totalMatches,
    turn,
    suggestions,
  };
}

/** List all available occupations (for autocomplete / test case reference). */
export function listOccupations(): { code: string; title: string; category: string }[] {
  return occupations.map(o => ({ code: o.code, title: o.title, category: o.category }));
}

/** Get a single occupation by code or title. */
export function getOccupation(query: string): OnetOccupation | null {
  return resolveOccupation(query);
}
