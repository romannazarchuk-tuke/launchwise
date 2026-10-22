import { ButtonLink } from "../components/ButtonLink";
import { useTitle } from "../lib/useTitle";

export default function NotFound() {
  useTitle("Page not found");
  return (
    <section className="container-page grid grid-cols-1 items-center gap-10 py-16 sm:py-24 md:grid-cols-12">
      <div className="md:col-span-7">
        <h1 className="text-[2.6rem] leading-[1.05] font-extrabold sm:text-5xl">Page not found</h1>
        <p className="mt-4 max-w-[34rem] text-lg text-muted">
          There's no page at this address. It may have moved, or the link has a typo.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <ButtonLink to="/planner">Build my website plan</ButtonLink>
          <ButtonLink to="/" variant="secondary">
            Back to home
          </ButtonLink>
        </div>
      </div>

      {/* a page that isn't in the sitemap: same visual language as the "later" cards */}
      <div className="md:col-span-5" aria-hidden="true">
        <div className="dot-grid mx-auto max-w-sm rounded-[28px] border border-line p-6">
          <div className="rounded-[14px] border border-lilac-ink/25 bg-lilac p-3">
            <p className="font-display font-semibold text-lilac-ink">Home</p>
          </div>
          <div className="mx-auto h-6 w-px bg-ink/20" />
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-[14px] border border-sky-ink/20 bg-sky p-3">
              <p className="font-display font-semibold text-sky-ink">Planner</p>
            </div>
            <div className="rotate-3 rounded-[14px] border-2 border-dashed border-ink/25 bg-white p-3">
              <p className="font-display font-semibold text-muted">404</p>
              <p className="text-sm text-muted">not in the plan</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
