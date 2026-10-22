/**
 * The one way page counts are described: "4 pages at launch + required Privacy & imprint, 4 later".
 * Mirrors backend/app/rules.py (split_pages, launch_group_text, page_counts_text) and uses the same
 * `priority` / `required` flags from the engine, so the website, the summary and the export always agree.
 */
import type { Page } from "../api";

const plural = (n: number, word: string) => (n === 1 ? `${n} ${word}` : `${n} ${word}s`);

/** "A", "A and B", "A, B and C" (same as the backend's _join). */
export function joinNames(names: string[]): string {
  if (names.length <= 1) return names.join("");
  return `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
}

export function splitPages(sitemap: Page[]) {
  return {
    launch: sitemap.filter((p) => p.priority === "launch" && !p.required),
    required: sitemap.filter((p) => p.required),
    later: sitemap.filter((p) => p.priority === "later"),
  };
}

/** Label of the Launch group, e.g. "4 pages + required Privacy & imprint". */
export function launchGroupText(sitemap: Page[]): string {
  const { launch, required } = splitPages(sitemap);
  const text = plural(launch.length, "page");
  return required.length ? `${text} + required ${joinNames(required.map((p) => p.name))}` : text;
}

/** Label of the Later group, e.g. "4 pages". */
export function laterGroupText(sitemap: Page[]): string {
  return plural(splitPages(sitemap).later.length, "page");
}

export function pageCountsText(sitemap: Page[]): string {
  const { launch, required, later } = splitPages(sitemap);
  let text = `${plural(launch.length, "page")} at launch`;
  if (required.length) text += ` + required ${joinNames(required.map((p) => p.name))}`;
  if (later.length) text += `, ${later.length} later`;
  return text;
}
