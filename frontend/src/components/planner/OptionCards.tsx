import { Check } from "lucide-react";
import { useId } from "react";
import type { Choice } from "../../api";
import { OptionIcon } from "../../lib/icons";

/**
 * Selectable cards built on real radio buttons / checkboxes: arrow keys move between
 * radios, Space toggles checkboxes, and screen readers announce "selected".
 * The input is visually hidden; the card shows its state and the focus ring.
 */

type Props<Id extends string> = {
  legend: string;
  hideLegend?: boolean;
  name: string;
  choices: Choice<Id>[];
  columns?: "2" | "3";
  compact?: boolean; // smaller cards without descriptions' extra space
} & (
  | { multiple?: false; value: Id | null; onChange: (id: Id) => void }
  | { multiple: true; value: Id[]; onChange: (ids: Id[]) => void }
);

const GRID = { "2": "sm:grid-cols-2", "3": "sm:grid-cols-2 lg:grid-cols-3" };

export function OptionCards<Id extends string>(props: Props<Id>) {
  const { legend, hideLegend, name, choices, columns = "3", compact } = props;
  const uid = useId(); // ids for aria-labelledby / aria-describedby
  const isChecked = (id: Id) => (props.multiple ? props.value.includes(id) : props.value === id);

  function toggle(id: Id) {
    if (props.multiple) {
      props.onChange(props.value.includes(id) ? props.value.filter((v) => v !== id) : [...props.value, id]);
    } else {
      props.onChange(id);
    }
  }

  return (
    <fieldset>
      <legend className={hideLegend ? "sr-only" : "mb-3 font-display text-lg font-semibold"}>{legend}</legend>
      <div className={`grid grid-cols-1 gap-3 ${GRID[columns]}`}>
        {choices.map((choice) => (
          <label
            key={choice.id}
            className={`group relative flex cursor-pointer items-start gap-3 rounded-[18px] border border-line bg-white shadow-soft transition-colors hover:border-violet/40 has-[:checked]:border-violet has-[:checked]:bg-violet-50/60 has-[:checked]:ring-1 has-[:checked]:ring-violet has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-3 has-[:focus-visible]:outline-violet ${
              compact ? "p-3.5" : "p-4"
            }`}
          >
            <input
              type={props.multiple ? "checkbox" : "radio"}
              name={name}
              value={choice.id}
              checked={isChecked(choice.id)}
              onChange={() => toggle(choice.id)}
              className="sr-only"
              // name = the label only; the description is read as extra help
              aria-labelledby={`${uid}-${choice.id}-label`}
              aria-describedby={choice.description ? `${uid}-${choice.id}-desc` : undefined}
            />
            {choice.icon && (
              <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-deep transition-colors group-has-[:checked]:bg-violet group-has-[:checked]:text-white">
                <OptionIcon name={choice.icon} />
              </span>
            )}
            <span className="min-w-0 flex-1 pr-6">
              <span id={`${uid}-${choice.id}-label`} className="block font-semibold leading-snug text-ink">
                {choice.label}
              </span>
              {choice.description && (
                <span id={`${uid}-${choice.id}-desc`} className="mt-0.5 block text-[0.9rem] leading-snug text-muted">
                  {choice.description}
                </span>
              )}
            </span>
            {/* state marker: round for single choice, square for multi-select */}
            <span
              aria-hidden="true"
              className={`absolute top-3.5 right-3.5 flex size-5 items-center justify-center border border-control bg-white text-white transition-colors group-has-[:checked]:border-violet group-has-[:checked]:bg-violet ${
                props.multiple ? "rounded-md" : "rounded-full"
              }`}
            >
              <Check className="size-3.5 opacity-0 group-has-[:checked]:opacity-100" strokeWidth={3} />
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
