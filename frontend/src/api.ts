/**
 * Typed client for the LaunchWise API (/api, proxied by nginx to FastAPI).
 * Types mirror backend/app/schemas.py — keep them in sync.
 */

// ---------- input ----------

export type BusinessType =
  | "coffee_shop" | "restaurant" | "beauty_salon" | "online_store"
  | "local_services" | "freelancer" | "consulting";
export type Goal = "bookings" | "sell_online" | "leads" | "brand" | "portfolio";
export type Audience = "local" | "national" | "international";
export type Language = "en" | "de" | "fr" | "es" | "it" | "pl" | "sk" | "cs" | "uk";
export type Feature =
  | "booking" | "payments" | "blog" | "gallery" | "reviews"
  | "map_hours" | "contact_form" | "multilingual" | "newsletter";
export type Budget = "starter" | "standard" | "advanced";
export type Timeline = "asap" | "one_month" | "flexible";

export interface PlanInput {
  business_type: BusinessType;
  goal: Goal;
  audience: Audience;
  languages: Language[];
  features: Feature[];
  budget: Budget;
  timeline: Timeline;
  business_name?: string | null;
}

// ---------- options (GET /api/options) ----------

export interface Choice<Id extends string = string> {
  id: Id;
  label: string;
  description?: string;
  icon?: string; // lucide icon name, e.g. "coffee"
}

export interface Options {
  business_types: Choice<BusinessType>[];
  goals: Choice<Goal>[];
  audiences: Choice<Audience>[];
  languages: Choice<Language>[];
  features: Choice<Feature>[];
  budgets: Choice<Budget>[];
  timelines: Choice<Timeline>[];
  limits: { languages_min: number; languages_max: number; business_name_max: number };
}

// ---------- generated plan ----------

export type SiteTypeId = "landing_page" | "business_site" | "booking_site" | "ecommerce" | "portfolio";

export interface Page {
  key: string; // stable page id from the rule engine, e.g. "home", "menu", "booking", "legal"
  name: string;
  slug: string;
  priority: "launch" | "later";
  required: boolean; // always launch, never counted in page totals (Privacy & imprint, Shipping & returns)
  sections: string[];
  why: string;
}

export interface FeatureItem {
  id: Feature;
  name: string;
  priority: "must" | "nice";
  recommended: boolean; // true = the user didn't pick it, the engine suggests it
  why: string;
}

export interface SeoItem {
  id: string;
  title: string;
  category: "basics" | "local" | "content" | "technical";
  why: string;
}

export interface PlanResult {
  summary: string;
  site_type: { id: SiteTypeId; name: string; why: string };
  complexity: { score: number; label: "Simple" | "Moderate" | "Complex"; estimated_weeks: string; why: string };
  sitemap: Page[];
  features: FeatureItem[];
  content_ideas: { page: string; ideas: string[] }[];
  seo_checklist: SeoItem[];
  next_steps: { title: string; why: string }[];
}

export interface PlanCreated {
  id: string;
  plan: PlanResult;
}

export interface SavedPlan {
  id: string;
  created_at: string;
  engine_version: string;
  input: PlanInput;
  plan: PlanResult;
}

// ---------- examples (GET /api/examples) ----------

export interface ExampleSite {
  domain: string;
  url: string;
  title: string;
  summary: string;
  dr: number | null; // Domain Rating 0–100 from FreeSerp; show as "Site authority"
}

export interface ExamplesResponse {
  items: ExampleSite[];
  source: "FreeSerp";
  cached: boolean;
}

// ---------- errors ----------

export interface FieldError {
  field: string;
  message: string;
}

/** Any failed API call. `status` is 0 when the server couldn't be reached at all. */
export class ApiError extends Error {
  readonly status: number;
  readonly fieldErrors: FieldError[];

  constructor(status: number, message: string, fieldErrors: FieldError[] = []) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.fieldErrors = fieldErrors;
  }

  get isNotFound(): boolean {
    return this.status === 404;
  }
}

// ---------- client ----------

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(BASE + path, {
      ...init,
      headers: { Accept: "application/json", ...(init?.body ? { "Content-Type": "application/json" } : {}) },
    });
  } catch {
    throw new ApiError(0, "Can't reach LaunchWise right now. Check your connection and try again.");
  }

  if (response.ok) {
    return (await response.json()) as T;
  }

  // Backend errors look like {"detail": "...", "errors": [{field, message}]}; nginx errors may be HTML.
  let detail = "Something went wrong on our side. Please try again in a moment.";
  let fieldErrors: FieldError[] = [];
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") detail = body.detail;
    if (Array.isArray(body?.errors)) fieldErrors = body.errors;
  } catch {
    if (response.status === 502 || response.status === 503 || response.status === 504) {
      detail = "LaunchWise is restarting or temporarily unavailable. Please try again in a moment.";
    }
  }
  throw new ApiError(response.status, detail, fieldErrors);
}

export const api = {
  getOptions: () => request<Options>("/options"),
  createPlan: (input: PlanInput) =>
    request<PlanCreated>("/plans", { method: "POST", body: JSON.stringify(input) }),
  getPlan: (id: string) => request<SavedPlan>(`/plans/${encodeURIComponent(id)}`),
  getExamples: (businessType: BusinessType) =>
    request<ExamplesResponse>(`/examples?business_type=${encodeURIComponent(businessType)}`),
  /** Plain link for downloads (the browser handles Content-Disposition). */
  exportUrl: (id: string, format: "md" | "txt") =>
    `${BASE}/plans/${encodeURIComponent(id)}/export?format=${format}`,
};
