import { Check } from "lucide-react";
import type { PlanResult } from "../../api";
import { pageColor } from "../../lib/pageColors";

export function ContentTab({ plan }: { plan: PlanResult }) {
  const keyOf = (pageName: string) => plan.sitemap.find((p) => p.name === pageName)?.key ?? "";
  return (
    <div>
      <p className="max-w-[42rem] text-muted">
        Ideas for what to write and show on each page that goes live first. Use them as a checklist when you collect content.
      </p>
      <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
        {plan.content_ideas.map((block) => {
          const color = pageColor(keyOf(block.page));
          return (
            <section key={block.page} className="rounded-[18px] border border-line bg-white p-5 shadow-soft">
              <h2 className="flex items-center gap-2 text-lg font-semibold">
                <span className={`size-3 rounded-full ${color.bg} ring-1 ${color.border}`} aria-hidden="true" />
                {block.page}
              </h2>
              <ul className="mt-3 space-y-2.5">
                {block.ideas.map((idea) => (
                  <li key={idea} className="flex gap-2.5 text-[0.95rem]">
                    <Check className="mt-1 size-4 shrink-0 text-violet" aria-hidden="true" />
                    {idea}
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
