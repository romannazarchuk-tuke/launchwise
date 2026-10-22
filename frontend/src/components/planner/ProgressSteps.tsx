import { REVIEW_STEP, STEPS } from "../../lib/plannerState";

/** Five labelled segments. Steps already reachable can be clicked to jump back. */
export function ProgressSteps({
  step,
  reachable,
  onGo,
}: {
  step: number;
  reachable: number; // highest step index the user may jump to
  onGo: (step: number) => void;
}) {
  const onReview = step === REVIEW_STEP;
  return (
    <nav aria-label="Planner progress">
      <ol className="grid grid-cols-5 gap-1.5 sm:gap-2">
        {STEPS.map((label, i) => {
          const done = i < step;
          const current = i === step;
          return (
            <li key={label}>
              <button
                type="button"
                onClick={() => onGo(i)}
                disabled={i > reachable || current}
                aria-current={current ? "step" : undefined}
                aria-label={`Step ${i + 1}: ${label}${done ? " (done)" : ""}`}
                className="group block w-full rounded-md py-1 text-left disabled:cursor-default"
              >
                <span
                  className={`block h-1.5 rounded-full transition-colors ${
                    done || current || onReview ? "bg-violet" : "bg-line"
                  } ${current ? "" : "group-enabled:group-hover:bg-violet-deep"}`}
                />
                <span
                  className={`mt-2 hidden text-sm font-medium sm:block ${
                    current ? "text-ink" : done || onReview ? "text-violet-deep" : "text-muted"
                  }`}
                >
                  {label}
                </span>
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
