/** LaunchWise mark: a tiny sitemap (one page branching into two). Same drawing as public/favicon.svg. */
export function LogoMark({ className = "size-7" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <rect width="32" height="32" rx="9" fill="#6D4AFF" />
      <path d="M16 11v5M9.5 16h13M9.5 16v5M22.5 16v5" stroke="#fff" strokeWidth="2" strokeLinecap="round" fill="none" />
      <rect x="11" y="6" width="10" height="6" rx="2" fill="#fff" />
      <rect x="5" y="20" width="9" height="6" rx="2" fill="#fff" fillOpacity=".85" />
      <rect x="18" y="20" width="9" height="6" rx="2" fill="#fff" fillOpacity=".85" />
    </svg>
  );
}

export function Wordmark() {
  return (
    <span className="flex items-center gap-2">
      <LogoMark />
      <span className="font-display text-[1.2rem] font-bold tracking-[-0.02em] text-ink">LaunchWise</span>
    </span>
  );
}
