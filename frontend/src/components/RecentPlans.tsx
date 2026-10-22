import { useEffect } from "react";
import { Link } from "react-router";
import { api, ApiError } from "../api";
import { clearRecentPlans, removeRecentPlan, useRecentPlans } from "../lib/recentPlans";

// Plans already checked in this page session, so each one is only verified once.
const verified = new Set<string>();

/** Remove stored plans that no longer exist on the server (404), quietly. */
function useDropMissingPlans(ids: string[]) {
  useEffect(() => {
    for (const id of ids) {
      if (verified.has(id)) continue;
      verified.add(id);
      api.getPlan(id).catch((err: unknown) => {
        if (err instanceof ApiError && err.isNotFound) removeRecentPlan(id);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- the joined string is the real dependency
  }, [ids.join(",")]);
}

const dateLabel = (iso: string) => {
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
};

/** Compact list of plans made in this browser. Renders nothing when there are none. */
export function RecentPlans({ excludeId, className = "" }: { excludeId?: string; className?: string }) {
  const all = useRecentPlans();
  const plans = all.filter((p) => p.id !== excludeId);
  useDropMissingPlans(plans.map((p) => p.id));

  if (plans.length === 0) return null;
  return (
    <section aria-labelledby="recent-plans-heading" className={`rounded-[18px] border border-line bg-white p-4 sm:p-5 ${className}`}>
      <div className="flex items-baseline justify-between gap-3">
        <h2 id="recent-plans-heading" className="text-lg font-semibold">
          Your recent plans
        </h2>
        <button
          type="button"
          onClick={clearRecentPlans}
          className="rounded-lg px-2 py-1 text-sm font-semibold text-muted hover:text-violet-deep"
        >
          Clear all
        </button>
      </div>
      <p className="text-sm text-muted">Saved only in this browser.</p>
      <ul className="mt-3 divide-y divide-line">
        {plans.map((plan) => (
          <li key={plan.id} className="flex items-center gap-2 py-2">
            <Link
              to={`/plan/${plan.id}`}
              className="group flex min-w-0 flex-1 flex-wrap items-baseline gap-x-2 rounded-lg px-1 py-1"
            >
              <span className="truncate font-semibold text-ink group-hover:text-violet-deep group-hover:underline group-hover:underline-offset-4">
                {plan.label}
              </span>
              <span className="text-sm text-muted">
                {plan.siteType}, {dateLabel(plan.createdAt)}
              </span>
            </Link>
            <button
              type="button"
              onClick={() => removeRecentPlan(plan.id)}
              className="shrink-0 rounded-lg px-2 py-1.5 text-sm font-semibold text-muted hover:bg-violet-50 hover:text-violet-deep"
            >
              Remove<span className="sr-only"> {plan.label} from recent plans</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
