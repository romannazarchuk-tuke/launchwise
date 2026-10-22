/** Planner wizard state: answers, step rules and sessionStorage persistence. */

import type { Audience, Budget, BusinessType, Feature, Goal, Language, Options, PlanInput, Timeline } from "../api";

export interface Answers {
  business_type: BusinessType | null;
  business_name: string;
  goal: Goal | null;
  audience: Audience | null;
  languages: Language[];
  features: Feature[];
  budget: Budget | null;
  timeline: Timeline | null;
}

export const EMPTY_ANSWERS: Answers = {
  business_type: null,
  business_name: "",
  goal: null,
  audience: null,
  languages: ["en"],
  features: [],
  budget: null,
  timeline: null,
};

export const STEPS = ["Business", "Goal", "Audience", "Features", "Budget"] as const;
export const REVIEW_STEP = STEPS.length; // the summary screen after the 5 steps

/** Why the user can't continue from this step yet, or null if the step is complete. */
export function stepProblem(step: number, a: Answers, limits: Options["limits"]): string | null {
  switch (step) {
    case 0:
      if (!a.business_type) return "Choose a business type to continue.";
      if (a.business_name.trim().length > limits.business_name_max)
        return `Keep the business name under ${limits.business_name_max} characters.`;
      return null;
    case 1:
      return a.goal ? null : "Choose the main goal to continue.";
    case 2:
      if (!a.audience) return "Choose where your customers are to continue.";
      if (a.languages.length < limits.languages_min) return "Choose at least one language.";
      if (a.languages.length > limits.languages_max) return `Choose up to ${limits.languages_max} languages.`;
      return null;
    case 3:
      return null; // features are optional: the engine recommends missing ones
    case 4:
      if (!a.budget) return "Choose a budget to continue.";
      if (!a.timeline) return "Choose a timeline to continue.";
      return null;
    default:
      return null;
  }
}

/** The first step that still needs an answer (or the review screen when all are done). */
export function firstIncompleteStep(a: Answers, limits: Options["limits"]): number {
  for (let step = 0; step < STEPS.length; step++) {
    if (stepProblem(step, a, limits)) return step;
  }
  return REVIEW_STEP;
}

export function toPlanInput(a: Answers): PlanInput {
  if (!a.business_type || !a.goal || !a.audience || !a.budget || !a.timeline) {
    throw new Error("Planner answers are incomplete");
  }
  return {
    business_type: a.business_type,
    goal: a.goal,
    audience: a.audience,
    languages: a.languages,
    features: a.features,
    budget: a.budget,
    timeline: a.timeline,
    business_name: a.business_name.trim() || null,
  };
}

/** Drop anything the server no longer offers (e.g. stored answers from an older version). */
export function sanitize(a: Answers, options: Options): Answers {
  const has = <T extends string>(list: { id: T }[], id: T | null) => (id && list.some((c) => c.id === id) ? id : null);
  const languages = a.languages.filter((id) => options.languages.some((c) => c.id === id));
  return {
    business_type: has(options.business_types, a.business_type),
    business_name: a.business_name.slice(0, options.limits.business_name_max),
    goal: has(options.goals, a.goal),
    audience: has(options.audiences, a.audience),
    languages: languages.length ? languages.slice(0, options.limits.languages_max) : EMPTY_ANSWERS.languages,
    features: a.features.filter((id) => options.features.some((c) => c.id === id)),
    budget: has(options.budgets, a.budget),
    timeline: has(options.timelines, a.timeline),
  };
}

// ---------- persistence (per browser tab) ----------

const STORAGE_KEY = "launchwise.planner.v1";

interface Stored {
  answers: Answers;
  step: number;
}

export function loadProgress(): Stored | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw) as Partial<Stored>;
    if (!data || typeof data !== "object" || typeof data.step !== "number" || !data.answers) return null;
    // Merge over the defaults so a missing field can't break the wizard.
    const answers = { ...EMPTY_ANSWERS, ...data.answers };
    if (!Array.isArray(answers.languages) || !Array.isArray(answers.features) || typeof answers.business_name !== "string") {
      return null;
    }
    return { answers, step: data.step };
  } catch {
    return null; // storage blocked (private mode) or corrupted JSON: start fresh
  }
}

export function saveProgress(answers: Answers, step: number) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ answers, step }));
  } catch {
    // storage full or blocked: the wizard still works, it just won't survive a reload
  }
}

export function clearProgress() {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
