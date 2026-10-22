import { Check } from "lucide-react";
import type { Choice, Language } from "../../api";

/** Toggle chips (real checkboxes) with a maximum: once full, the other chips are disabled. */
export function LanguageChips({
  choices,
  value,
  max,
  onChange,
}: {
  choices: Choice<Language>[];
  value: Language[];
  max: number;
  onChange: (value: Language[]) => void;
}) {
  const full = value.length >= max;
  return (
    <fieldset>
      <legend className="mb-1 font-display text-lg font-semibold">Which languages should the site have?</legend>
      <p id="languages-hint" className="mb-3 text-[0.95rem] text-muted">
        Choose up to {max}. {full ? `That's the maximum. Remove one to pick another.` : ""}
      </p>
      <div className="flex flex-wrap gap-2" aria-describedby="languages-hint">
        {choices.map((choice) => {
          const checked = value.includes(choice.id);
          const disabled = !checked && full;
          return (
            <label
              key={choice.id}
              className={`inline-flex h-10 items-center gap-1.5 rounded-full border px-4 text-[0.95rem] font-medium transition-colors has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-3 has-[:focus-visible]:outline-violet ${
                checked
                  ? "border-violet bg-violet text-white"
                  : disabled
                    ? "cursor-not-allowed border-line bg-paper text-muted/60"
                    : "cursor-pointer border-line bg-white text-ink hover:border-violet/40"
              }`}
            >
              <input
                type="checkbox"
                className="sr-only"
                checked={checked}
                disabled={disabled}
                onChange={() => onChange(checked ? value.filter((v) => v !== choice.id) : [...value, choice.id])}
              />
              {checked && <Check className="size-4" strokeWidth={3} aria-hidden="true" />}
              {choice.label}
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
