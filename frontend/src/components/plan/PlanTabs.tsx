import { useEffect, useRef, type KeyboardEvent } from "react";

export const TABS = [
  { id: "overview", label: "Overview" },
  { id: "sitemap", label: "Sitemap" },
  { id: "features", label: "Features" },
  { id: "content", label: "Content" },
  { id: "seo", label: "SEO checklist" },
  { id: "examples", label: "Examples" },
] as const;

export type TabId = (typeof TABS)[number]["id"];

export const isTabId = (value: string | null): value is TabId => TABS.some((t) => t.id === value);

/** ARIA tabs: arrow keys / Home / End move between tabs; scrolls sideways on phones. */
export function PlanTabs({ active, onChange }: { active: TabId; onChange: (tab: TabId) => void }) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});
  const stripRef = useRef<HTMLDivElement>(null);

  // Keep the active tab visible in the strip. Only the strip scrolls sideways; the page itself
  // must not move (scrollIntoView would scroll the page down to the tabs on phones).
  useEffect(() => {
    const strip = stripRef.current;
    const tab = refs.current[active];
    if (!strip || !tab) return;
    const left = tab.getBoundingClientRect().left - strip.getBoundingClientRect().left + strip.scrollLeft;
    if (left < strip.scrollLeft || left + tab.offsetWidth > strip.scrollLeft + strip.clientWidth) {
      strip.scrollTo({ left: Math.max(0, left - 16) });
    }
  }, [active]);

  function onKeyDown(event: KeyboardEvent) {
    const index = TABS.findIndex((t) => t.id === active);
    const target = {
      ArrowRight: (index + 1) % TABS.length,
      ArrowLeft: (index - 1 + TABS.length) % TABS.length,
      Home: 0,
      End: TABS.length - 1,
    }[event.key];
    if (target === undefined) return;
    event.preventDefault();
    onChange(TABS[target].id);
    refs.current[TABS[target].id]?.focus();
  }

  return (
    <div className="sticky top-16 z-20 -mx-4 border-b border-line bg-paper/95 px-4 backdrop-blur sm:mx-0 sm:px-0">
      <div ref={stripRef} role="tablist" aria-label="Plan sections" onKeyDown={onKeyDown} className="flex gap-1 overflow-x-auto [scrollbar-width:none]">
        {TABS.map((tab) => {
          const selected = tab.id === active;
          return (
            <button
              key={tab.id}
              ref={(el) => {
                refs.current[tab.id] = el;
              }}
              type="button"
              role="tab"
              id={`tab-${tab.id}`}
              aria-selected={selected}
              aria-controls={`panel-${tab.id}`}
              tabIndex={selected ? 0 : -1}
              onClick={() => onChange(tab.id)}
              className={`relative shrink-0 rounded-t-lg px-3.5 py-3.5 text-[0.95rem] font-semibold whitespace-nowrap transition-colors ${
                selected ? "text-violet-deep" : "text-muted hover:text-ink"
              }`}
            >
              {tab.label}
              {selected && <span className="absolute inset-x-2 bottom-0 h-[3px] rounded-full bg-violet" aria-hidden="true" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
