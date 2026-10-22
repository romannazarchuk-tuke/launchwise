import type { Page } from "../../api";
import { launchGroupText, laterGroupText, pageCountsText, splitPages } from "../../lib/pageCounts";
import { pageColor } from "../../lib/pageColors";

/**
 * Home on top, then the pages that go live with it, then the ones that can wait.
 * Filled cards = launch, dashed cards = later. Colours come from the engine's page keys.
 */
export function SitemapTab({ sitemap }: { sitemap: Page[] }) {
  const { launch, required, later } = splitPages(sitemap);
  const home = launch.find((p) => p.key === "home");
  const children = launch.filter((p) => p.key !== "home");

  return (
    <div>
      <p className="text-muted">
        <span className="font-semibold text-ink" data-testid="sitemap-counts">{pageCountsText(sitemap)}</span>. Filled cards go
        live first. Dashed cards can wait.
      </p>

      <section aria-labelledby="launch-heading" className="mt-5 rounded-[28px] border border-line bg-white p-4 shadow-soft sm:p-6">
        <GroupHeading id="launch-heading" title="Launch now" detail={launchGroupText(sitemap)} />
        {home && (
          <div className="mx-auto mt-4 max-w-2xl">
            <PageCard page={home} />
          </div>
        )}
        {(children.length > 0 || required.length > 0) && (
          <>
            {home && <div className="mx-auto h-6 w-px bg-ink/20" aria-hidden="true" />}
            <ul className="grid grid-cols-1 gap-3 border-t border-dashed border-ink/15 pt-6 sm:grid-cols-2 lg:grid-cols-3">
              {[...children, ...required].map((page) => (
                <li key={page.key}>
                  <PageCard page={page} />
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      {later.length > 0 && (
        <section aria-labelledby="later-heading" className="mt-5 rounded-[28px] border-2 border-dashed border-ink/15 p-4 sm:p-6">
          <GroupHeading id="later-heading" title="Later" detail={laterGroupText(sitemap)} />
          <ul className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {later.map((page) => (
              <li key={page.key}>
                <PageCard page={page} />
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function GroupHeading({ id, title, detail }: { id: string; title: string; detail: string }) {
  return (
    <h2 id={id} className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-xl font-semibold">
      {title}
      <span className="font-sans text-[0.95rem] font-medium text-muted" data-testid={`${id}-count`}>
        {detail}
      </span>
    </h2>
  );
}

function PageCard({ page }: { page: Page }) {
  const color = pageColor(page.key);
  const later = page.priority === "later";
  return (
    <article
      className={`flex h-full flex-col rounded-[18px] border p-4 ${
        later ? "border-dashed border-ink/25 bg-white" : `${color.bg} ${color.border}`
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className={`flex items-center gap-2 text-lg leading-tight font-semibold ${color.ink}`}>
          {later && <span className={`size-2.5 shrink-0 rounded-full ${color.bg} ring-1 ${color.border}`} aria-hidden="true" />}
          {page.name}
        </h3>
        {page.required && (
          <span className="shrink-0 rounded-full bg-white/80 px-2 py-0.5 text-xs font-semibold text-stone-ink">Required</span>
        )}
      </div>
      <p className="mt-0.5 text-sm text-muted">{page.slug}</p>
      <ul className="mt-3 flex flex-wrap gap-1.5" aria-label={`Sections of ${page.name}`}>
        {page.sections.map((section) => (
          <li
            key={section}
            className={`rounded-full px-2.5 py-0.5 text-[0.8rem] font-medium ${
              later ? "border border-line text-muted" : "bg-white/85 text-ink/80"
            }`}
          >
            {section}
          </li>
        ))}
      </ul>
      <p className={`mt-3 text-[0.9rem] leading-snug ${later ? "text-muted" : "text-ink/75"}`}>{page.why}</p>
    </article>
  );
}
