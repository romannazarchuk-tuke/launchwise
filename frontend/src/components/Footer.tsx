import { Link } from "react-router";
import { Wordmark } from "./Logo";

export function Footer() {
  return (
    <footer className="mt-16 sm:mt-20 border-t border-line bg-white">
      <div className="container-page flex flex-col gap-6 py-10 sm:flex-row sm:items-start sm:justify-between">
        <div className="max-w-sm">
          <Wordmark />
          <p className="mt-3 text-sm text-muted">
            Recommendations are rule-based. Site examples powered by{" "}
            <a href="https://freeserp.ai" className="underline decoration-line underline-offset-4 hover:text-violet-deep">
              FreeSerp
            </a>
            .
          </p>
        </div>
        <nav aria-label="Footer" className="flex flex-wrap gap-x-6 gap-y-2 text-sm font-medium text-muted">
          <Link to="/planner" className="hover:text-violet-deep">Planner</Link>
          <Link to="/#how-it-works" className="hover:text-violet-deep">How it works</Link>
          <Link to="/about" className="hover:text-violet-deep">About</Link>
        </nav>
      </div>
      <div className="container-page pb-8 text-sm text-muted">© 2026 LaunchWise</div>
    </footer>
  );
}
