import type { ReactNode } from "react";

/** Circular gauge (SEO progress, complexity score). Content in the middle is optional. */
export function ProgressRing({
  value,
  max,
  size = 44,
  stroke = 4,
  children,
  label,
}: {
  value: number;
  max: number;
  size?: number;
  stroke?: number;
  children?: ReactNode;
  label?: string; // accessible description, e.g. "5 of 12 done"
}) {
  const r = 18 - stroke / 2;
  const circumference = 2 * Math.PI * r;
  const share = max > 0 ? Math.min(1, value / max) : 0;
  return (
    <span className="relative inline-flex shrink-0" style={{ width: size, height: size }} role={label ? "img" : undefined} aria-label={label}>
      <svg viewBox="0 0 36 36" className="size-full -rotate-90" aria-hidden="true">
        <circle cx="18" cy="18" r={r} fill="none" stroke="var(--color-line)" strokeWidth={stroke} />
        <circle
          cx="18" cy="18" r={r} fill="none" stroke="var(--color-violet)" strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={`${share * circumference} ${circumference}`}
          className="transition-[stroke-dasharray] duration-500"
        />
      </svg>
      {children && <span className="absolute inset-0 flex items-center justify-center" aria-hidden="true">{children}</span>}
    </span>
  );
}
