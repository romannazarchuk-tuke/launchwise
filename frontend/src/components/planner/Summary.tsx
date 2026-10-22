import { Pencil } from "lucide-react";
import type { Choice, Options } from "../../api";
import type { Answers } from "../../lib/plannerState";

const labelOf = <Id extends string>(list: Choice<Id>[], id: Id | null) => list.find((c) => c.id === id)?.label ?? "—";

/** Review screen: every answer with an Edit button that jumps back to its step. */
export function Summary({ answers, options, onEdit }: { answers: Answers; options: Options; onEdit: (step: number) => void }) {
  const rows: { step: number; label: string; value: string }[] = [
    {
      step: 0,
      label: "Business",
      value:
        labelOf(options.business_types, answers.business_type) +
        (answers.business_name.trim() ? `, "${answers.business_name.trim()}"` : ""),
    },
    { step: 1, label: "Main goal", value: labelOf(options.goals, answers.goal) },
    {
      step: 2,
      label: "Audience",
      value: `${labelOf(options.audiences, answers.audience)}, in ${answers.languages
        .map((id) => labelOf(options.languages, id))
        .join(", ")}`,
    },
    {
      step: 3,
      label: "Features",
      value: answers.features.length
        ? answers.features.map((id) => labelOf(options.features, id)).join(", ")
        : "None picked. We'll recommend the ones you need.",
    },
    {
      step: 4,
      label: "Budget and timeline",
      value: `${labelOf(options.budgets, answers.budget)}, ${labelOf(options.timelines, answers.timeline).toLowerCase()}`,
    },
  ];

  return (
    <dl className="divide-y divide-line rounded-[18px] border border-line">
      {rows.map((row) => (
        <div key={row.label} className="flex items-start gap-4 px-4 py-4 sm:px-5">
          <div className="min-w-0 flex-1 sm:flex sm:gap-6">
            <dt className="shrink-0 text-sm font-medium text-muted sm:w-44 sm:text-[0.95rem]">{row.label}</dt>
            <dd className="mt-0.5 font-medium text-ink sm:mt-0">{row.value}</dd>
          </div>
          <button
            type="button"
            onClick={() => onEdit(row.step)}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg px-2 py-1 text-sm font-semibold text-violet-deep hover:bg-violet-50"
          >
            <Pencil className="size-3.5" aria-hidden="true" />
            Edit<span className="sr-only"> {row.label.toLowerCase()}</span>
          </button>
        </div>
      ))}
    </dl>
  );
}
