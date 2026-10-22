import { useId } from "react";

const EXPLANATION = "Domain Rating from FreeSerp: how established the site is.";

/** FreeSerp's DR shown in plain words, with an explanation on hover and keyboard focus. */
export function AuthorityBadge({ dr }: { dr: number | null }) {
  const tipId = useId();
  if (dr === null) return null;
  return (
    <span className="group relative inline-flex">
      <span
        tabIndex={0}
        aria-describedby={tipId}
        className="cursor-help whitespace-nowrap rounded-full border border-line bg-white px-2.5 py-1 text-xs font-semibold text-muted"
      >
        Site authority {dr}/100
      </span>
      <span
        id={tipId}
        role="tooltip"
        className="pointer-events-none absolute bottom-full left-0 z-10 mb-2 w-56 rounded-lg bg-ink px-3 py-2 text-xs leading-snug font-medium text-white opacity-0 shadow-lift transition-opacity group-focus-within:opacity-100 group-hover:opacity-100"
      >
        {EXPLANATION}
      </span>
    </span>
  );
}
