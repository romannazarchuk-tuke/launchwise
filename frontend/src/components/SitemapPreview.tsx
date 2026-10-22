import type { CSSProperties } from "react";
import { pageColor } from "../lib/pageColors";

/**
 * Hero illustration: a real LaunchWise plan in miniature (the coffee-shop scenario from the
 * rule engine tests). Built from HTML so it stays sharp and readable at any size.
 * The page-load sequence (lines, then cards) is the only ambient animation on the site.
 */

type MiniPage = { key: string; name: string; sections: string[] };

const HOME: MiniPage = { key: "home", name: "Home", sections: ["Hero", "Menu highlights", "Booking widget", "Map & hours"] };
const CHILDREN: MiniPage[] = [
  { key: "menu", name: "Menu", sections: ["Categories", "Prices", "Dietary info"] },
  { key: "booking", name: "Reserve a table", sections: ["Booking widget", "FAQ"] },
  { key: "visit", name: "Visit us", sections: ["Map & hours", "Directions"] },
];
const LATER = ["Our story", "Events", "Gallery"];

const delay = (ms: number): CSSProperties => ({ animationDelay: `${ms}ms` });

function PageCard({ page, style }: { page: MiniPage; style?: CSSProperties }) {
  const color = pageColor(page.key);
  return (
    <div
      className={`animate-plan-in rounded-[14px] border ${color.border} ${color.bg} p-3 shadow-soft`}
      style={style}
    >
      <p className={`font-display text-[0.95rem] font-semibold leading-tight ${color.ink}`}>{page.name}</p>
      <ul className="mt-2 flex flex-wrap gap-1">
        {page.sections.map((section) => (
          <li key={section} className="rounded-full bg-white/80 px-2 py-0.5 text-[0.72rem] font-medium text-ink/75">
            {section}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function SitemapPreview() {
  return (
    <figure className="dot-grid relative rounded-[28px] border border-line p-4 shadow-lift sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="font-display text-lg font-semibold leading-tight">Bean There</p>
          <p className="text-sm text-muted">Coffee shop plan</p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          <span className="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-semibold text-violet-deep">Booking website</span>
          <span className="rounded-full border border-line bg-white px-2.5 py-1 text-xs font-semibold text-muted">4/10 Moderate</span>
        </div>
      </div>

      {/* the tree */}
      <div className="mt-5">
        <div className="mx-auto sm:max-w-[19rem]">
          <PageCard page={HOME} style={delay(80)} />
        </div>
        {/* stem down from Home (desktop only) */}
        <div className="animate-line-in mx-auto hidden h-5 w-px bg-ink/20 sm:block" style={delay(300)} />

        <div className="relative mt-3 border-l border-ink/15 pl-4 sm:mt-0 sm:grid sm:grid-cols-3 sm:gap-3 sm:border-l-0 sm:pl-0">
          {/* horizontal bar joining the three children (desktop only) */}
          <div
            className="animate-line-in absolute top-0 right-[16.67%] left-[16.67%] hidden h-px bg-ink/20 sm:block"
            style={delay(380)}
          />
          {CHILDREN.map((page, i) => (
            <div key={page.key} className="relative mt-3 first:mt-0 sm:mt-0 sm:pt-5">
              <span
                className="animate-line-in absolute top-0 left-1/2 hidden h-5 w-px bg-ink/20 sm:block"
                style={delay(420)}
              />
              {/* tick from the side line (mobile only) */}
              <span className="absolute top-6 -left-4 h-px w-4 bg-ink/15 sm:hidden" />
              <PageCard page={page} style={delay(480 + i * 90)} />
            </div>
          ))}
        </div>
      </div>

      <div className="animate-plan-in mt-5 flex flex-wrap items-center gap-2" style={delay(820)}>
        <span className="text-sm font-medium text-muted">Later</span>
        {LATER.map((name) => (
          <span key={name} className="rounded-full border border-dashed border-ink/25 bg-white px-2.5 py-1 text-xs font-medium text-muted">
            {name}
          </span>
        ))}
      </div>

      <figcaption className="sr-only">
        Example plan for a coffee shop that wants table bookings: Home, Menu, Reserve a table and Visit us at launch;
        Our story, Events and Gallery later.
      </figcaption>
    </figure>
  );
}
