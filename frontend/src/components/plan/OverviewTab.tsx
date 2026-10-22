import type { PlanResult } from "../../api";
import { ProgressRing } from "../ProgressRing";

export function OverviewTab({ plan }: { plan: PlanResult }) {
  const { site_type, complexity, next_steps } = plan;
  const weeks = complexity.estimated_weeks === "1" ? "about 1 week" : `about ${complexity.estimated_weeks} weeks`;
  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
      <div className="space-y-5">
        <section className="rounded-[18px] border border-line bg-white p-5 shadow-soft sm:p-6">
          <h2 className="text-xl font-semibold">Site type</h2>
          <span className="mt-3 inline-block rounded-full bg-violet-50 px-3 py-1 text-sm font-semibold text-violet-deep">
            {site_type.name}
          </span>
          <p className="mt-3 text-muted">{site_type.why}</p>
        </section>

        <section className="rounded-[18px] border border-line bg-white p-5 shadow-soft sm:p-6">
          <h2 className="text-xl font-semibold">Complexity</h2>
          <div className="mt-4 flex items-center gap-4">
            <ProgressRing value={complexity.score} max={10} size={64} label={`Complexity ${complexity.score} out of 10`}>
              <span className="font-display text-xl font-bold">{complexity.score}</span>
            </ProgressRing>
            <div>
              <p className="font-semibold">
                {complexity.label}: {complexity.score} out of 10
              </p>
              <p className="text-muted">Building it takes {weeks}.</p>
            </div>
          </div>
          <p className="mt-4 rounded-xl bg-paper px-4 py-3 text-[0.95rem] text-muted">How we scored it: {complexity.why}</p>
        </section>
      </div>

      <section className="rounded-[18px] border border-line bg-white p-5 shadow-soft sm:p-6">
        <h2 className="text-xl font-semibold">Next steps</h2>
        <ol className="mt-4 space-y-5">
          {next_steps.map((step, i) => (
            <li key={step.title} className="flex gap-3">
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-violet font-display text-sm font-bold text-white">
                {i + 1}
              </span>
              <div>
                <p className="font-semibold leading-snug">{step.title}</p>
                <p className="mt-1 text-[0.95rem] text-muted">{step.why}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
