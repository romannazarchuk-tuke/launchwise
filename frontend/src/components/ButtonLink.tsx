import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Link } from "react-router";

type Variant = "primary" | "secondary" | "inverse";
type Size = "md" | "lg";

const STYLES: Record<Variant, string> = {
  primary: "bg-violet text-white shadow-soft hover:bg-violet-deep disabled:bg-violet/40 disabled:shadow-none",
  secondary: "border border-line bg-white text-ink hover:border-violet/40 hover:text-violet-deep",
  inverse: "bg-white text-violet-deep hover:bg-violet-50",
};

const SIZES: Record<Size, string> = {
  md: "h-11 px-5 text-[0.95rem]",
  lg: "h-13 px-6 text-base",
};

/** Shared look for links and buttons, so both read as the same kind of control. */
export function buttonClass(variant: Variant = "primary", size: Size = "md", extra = "") {
  return `inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-colors disabled:cursor-not-allowed ${SIZES[size]} ${STYLES[variant]} ${extra}`;
}

/** A link that looks like a button (navigation, so it's an <a>, not a <button>). */
export function ButtonLink({
  to,
  children,
  variant = "primary",
  size = "md",
  className = "",
}: {
  to: string;
  children: ReactNode;
  variant?: Variant;
  size?: Size;
  className?: string;
}) {
  return (
    <Link to={to} className={buttonClass(variant, size, className)}>
      {children}
    </Link>
  );
}

/** An action button with the same look. */
export function Button({
  variant = "primary",
  size = "md",
  className = "",
  type = "button",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }) {
  return <button type={type} className={buttonClass(variant, size, className)} {...props} />;
}
