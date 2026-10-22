/** Which SEO checklist items are done, per plan, in localStorage. Storage errors are ignored. */

const key = (planId: string) => `launchwise.seo.${planId}`;

export function loadSeoDone(planId: string): string[] {
  try {
    const value = JSON.parse(localStorage.getItem(key(planId)) ?? "[]");
    return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
  } catch {
    return [];
  }
}

export function saveSeoDone(planId: string, done: string[]) {
  try {
    if (done.length) localStorage.setItem(key(planId), JSON.stringify(done));
    else localStorage.removeItem(key(planId));
  } catch {
    // private mode or full storage: the checklist still works for this visit
  }
}
