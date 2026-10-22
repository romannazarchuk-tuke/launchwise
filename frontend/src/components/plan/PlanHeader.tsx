import type { SavedPlan } from "../../api";
import { pageCountsText } from "../../lib/pageCounts";
import { ProgressRing } from "../ProgressRing";

/** Title, summary and the "At a glance" card. */
export function PlanHeader({ saved, businessLabel }: { saved: SavedPlan; businessLabel: string }) {
  const { plan, input } = saved;
  const { complexity } = plan;
  const weeks = complexity.estimated_weeks === "1" ? "About 1 week" : `About ${complexity.estimated_weeks} weeks`;

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 lg:gap-10">
      <div className="lg:col-span-8">
        <p className="text-sm font-medium text-muted">{businessLabel} plan</p>
        <h1 className="mt-1 text-[2.4rem] leading-[1.05] font-extrabold sm:text-[3.2rem]">
          {input.business_name || businessLabel}
        </h1>
        <p className="mt-5 max-w-[42rem] text-[1.05rem] text-ink/85">{plan.summary}</p>
      </div>

      <aside aria-label="At a glance" className="self-start rounded-[18px] border border-line bg-white p-5 shadow-soft lg:col-span-4">
        <h2 className="font-display text-lg font-semibold">At a glance</h2>
        <span className="mt-3 inline-block rounded-full bg-violet-50 px-3 py-1 text-sm font-semibold text-violet-deep">
          {plan.site_type.name}
        </span>
        <div className="mt-4 flex items-center gap-3">
          <ProgressRing value={complexity.score} max={10} size={52} label={`Complexity ${complexity.score} out of 10`}>
            <span className="font-display text-base font-bold">{complexity.score}</span>
          </ProgressRing>
          <div>
            <p className="font-semibold">{complexity.label} build</p>
            <p className="text-sm text-muted">{weeks}</p>
          </div>
        </div>
        <p className="mt-4 border-t border-line pt-4 text-[0.95rem]" data-testid="page-counts">
          {pageCountsText(plan.sitemap)}
        </p>
      </aside>
    </div>
  );
}
