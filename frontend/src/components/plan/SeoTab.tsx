import { useEffect, useState } from "react";
import type { SeoItem } from "../../api";
import { loadSeoDone, saveSeoDone } from "../../lib/seoProgress";
import { ProgressRing } from "../ProgressRing";

const CATEGORIES = [
  { id: "basics", title: "Basics" },
  { id: "local", title: "Local" },
  { id: "content", title: "Content" },
  { id: "technical", title: "Technical" },
] as const;

/** The checklist, ticked off item by item; progress is remembered per plan in this browser. */
export function SeoTab({ planId, items }: { planId: string; items: SeoItem[] }) {
  const [done, setDone] = useState<string[]>(() => loadSeoDone(planId).filter((id) => items.some((i) => i.id === id)));

  useEffect(() => saveSeoDone(planId, done), [planId, done]);

  const toggle = (id: string) => setDone((d) => (d.includes(id) ? d.filter((x) => x !== id) : [...d, id]));
  const count = done.length;
  const status =
    count === 0
      ? "Tick items off as you do them. Your progress is saved in this browser."
      : count === items.length
        ? "All done. Check Search Console in a few weeks to see the results."
        : "Nice progress. Your ticks are saved in this browser.";

  return (
    <div>
      <div className="flex flex-col gap-4 rounded-[18px] border border-line bg-white p-5 shadow-soft sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <ProgressRing value={count} max={items.length} size={64} label={`${count} of ${items.length} done`}>
            <span className="font-display text-sm font-bold">{Math.round((count / items.length) * 100)}%</span>
          </ProgressRing>
          <div>
            <p className="font-display text-xl font-semibold" data-testid="seo-progress">
              {count} of {items.length} done
            </p>
            <p className="text-[0.95rem] text-muted">{status}</p>
          </div>
        </div>
        {count > 0 && (
          <button
            type="button"
            onClick={() => setDone([])}
            className="self-start rounded-lg px-2 py-1 text-sm font-semibold text-muted hover:text-violet-deep sm:self-auto"
          >
            Clear checklist
          </button>
        )}
      </div>

      <div className="mt-6 space-y-7">
        {CATEGORIES.map((cat) => {
          const group = items.filter((i) => i.category === cat.id);
          if (group.length === 0) return null;
          return (
            <section key={cat.id}>
              <h2 className="text-lg font-semibold">{cat.title}</h2>
              <ul className="mt-3 space-y-2">
                {group.map((item) => (
                  <li key={item.id}>
                    <label className="group flex cursor-pointer gap-3 rounded-[14px] border border-line bg-white p-4 transition-colors hover:border-violet/40 has-[:checked]:bg-violet-50/50 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-violet">
                      <input
                        type="checkbox"
                        checked={done.includes(item.id)}
                        onChange={() => toggle(item.id)}
                        className="mt-0.5 size-5 shrink-0 accent-violet focus-visible:outline-none"
                      />
                      <span>
                        <span className="block font-semibold group-has-[:checked]:text-muted group-has-[:checked]:line-through">{item.title}</span>
                        <span className="mt-0.5 block text-[0.95rem] text-muted">{item.why}</span>
                      </span>
                    </label>
                  </li>
                ))}
              </ul>
            </section>
          );
        })}
      </div>
    </div>
  );
}
