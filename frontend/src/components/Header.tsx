import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router";
import { ButtonLink } from "./ButtonLink";
import { Wordmark } from "./Logo";

const NAV = [
  { to: "/#how-it-works", label: "How it works" },
  { to: "/planner", label: "Planner" },
  { to: "/about", label: "About" },
];

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-lg px-3 py-2 text-[0.95rem] font-medium transition-colors hover:text-violet-deep ${
    isActive ? "text-violet-deep" : "text-muted"
  }`;

export function Header() {
  const [open, setOpen] = useState(false);
  const location = useLocation();

  // Close the mobile menu after navigating.
  useEffect(() => setOpen(false), [location.pathname, location.hash]);

  return (
    <header className="sticky top-0 z-30 border-b border-line/70 bg-paper/85 backdrop-blur">
      <div className="container-page flex h-16 items-center justify-between gap-4">
        <Link to="/" aria-label="LaunchWise home" className="rounded-lg">
          <Wordmark />
        </Link>

        <nav aria-label="Main" className="hidden items-center gap-1 md:flex">
          {NAV.map((item) =>
            item.to.includes("#") ? (
              <Link key={item.to} to={item.to} className={linkClass({ isActive: false })}>
                {item.label}
              </Link>
            ) : (
              <NavLink key={item.to} to={item.to} className={linkClass}>
                {item.label}
              </NavLink>
            ),
          )}
        </nav>

        <div className="flex items-center gap-2">
          {/* wrapper hides it on phones: ButtonLink's own inline-flex would override "hidden" */}
          <div className="hidden sm:block">
            <ButtonLink to="/planner">Build my plan</ButtonLink>
          </div>
          <button
            type="button"
            className="inline-flex size-11 items-center justify-center rounded-xl border border-line bg-white text-ink md:hidden"
            aria-expanded={open}
            aria-controls="mobile-menu"
            aria-label={open ? "Close menu" : "Open menu"}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
      </div>

      {open && (
        <nav id="mobile-menu" aria-label="Main" className="border-t border-line bg-paper md:hidden">
          <div className="container-page flex flex-col gap-1 py-3">
            {NAV.map((item) => (
              <Link key={item.to} to={item.to} className="rounded-lg px-3 py-3 font-medium text-ink hover:bg-violet-50">
                {item.label}
              </Link>
            ))}
            <ButtonLink to="/planner" className="mt-2">
              Build my plan
            </ButtonLink>
          </div>
        </nav>
      )}
    </header>
  );
}
