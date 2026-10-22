import { useCallback, useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router";
import { api, ApiError, type Options, type SavedPlan } from "../api";
import { Button, ButtonLink } from "../components/ButtonLink";
import { ActionBar } from "../components/plan/ActionBar";
import { ContentTab } from "../components/plan/ContentTab";
import { ExamplesTab } from "../components/plan/ExamplesTab";
import { FeaturesTab } from "../components/plan/FeaturesTab";
import { OverviewTab } from "../components/plan/OverviewTab";
import { PlanHeader } from "../components/plan/PlanHeader";
import { isTabId, PlanTabs, type TabId } from "../components/plan/PlanTabs";
import { SeoTab } from "../components/plan/SeoTab";
import { SitemapTab } from "../components/plan/SitemapTab";
import { RecentPlans } from "../components/RecentPlans";
import { removeRecentPlan } from "../lib/recentPlans";
import { useTitle } from "../lib/useTitle";
import { useToast } from "../lib/useToast";

type State =
  | { status: "loading" }
  | { status: "not-found" }
  | { status: "error"; message: string }
  | { status: "ready"; saved: SavedPlan; options: Options | null };

/** Saved plans are personal: keep them out of search engines while one is open. */
function useNoIndex() {
  useEffect(() => {
    const meta = document.createElement("meta");
    meta.name = "robots";
    meta.content = "noindex";
    document.head.appendChild(meta);
    return () => meta.remove();
  }, []);
}

const prettify = (id: string) => id.charAt(0).toUpperCase() + id.slice(1).replace(/_/g, " ");

export default function Plan() {
  const { id = "" } = useParams();
  const [params, setParams] = useSearchParams();
  const [state, setState] = useState<State>({ status: "loading" });
  const { notify, toast } = useToast();
  useNoIndex();

  const tabParam = params.get("tab");
  const tab: TabId = isTabId(tabParam) ? tabParam : "overview";
  const setTab = (next: TabId) => setParams(next === "overview" ? {} : { tab: next }, { replace: true });

  const load = useCallback(() => {
    setState({ status: "loading" });
    // Options only provide labels and icons, so the page still works if they fail.
    Promise.all([api.getPlan(id), api.getOptions().catch(() => null)])
      .then(([saved, options]) => setState({ status: "ready", saved, options }))
      .catch((err: unknown) => {
        if (err instanceof ApiError && (err.status === 404 || err.status === 422)) {
          removeRecentPlan(id); // a plan that no longer exists shouldn't stay in "Your recent plans"
          setState({ status: "not-found" });
        }
        else setState({ status: "error", message: err instanceof ApiError ? err.message : "Something went wrong." });
      });
  }, [id]);

  useEffect(load, [load]);

  const ready = state.status === "ready" ? state : null;
  const businessLabel = ready
    ? (ready.options?.business_types.find((b) => b.id === ready.saved.input.business_type)?.label ??
      prettify(ready.saved.input.business_type))
    : "";
  useTitle(
    ready
      ? `${ready.saved.input.business_name || businessLabel} website plan`
      : state.status === "not-found"
        ? "Plan not found"
        : "Your website plan",
  );

  if (state.status === "loading") return <PlanSkeleton />;
  if (state.status === "not-found") return <NotFoundState />;
  if (state.status === "error") return <ErrorState message={state.message} onRetry={load} />;

  const { saved, options } = state;
  const created = new Date(saved.created_at + (saved.created_at.endsWith("Z") ? "" : "Z")).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="container-page pt-8 pb-4 sm:pt-12">
      <PlanHeader saved={saved} businessLabel={businessLabel} />
      <div className="mt-7">
        <ActionBar planId={saved.id} notify={notify} />
      </div>

      <div className="mt-8">
        <PlanTabs active={tab} onChange={setTab} />
        <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`} tabIndex={0} className="pt-7 focus-visible:outline-offset-8">
          {tab === "overview" && <OverviewTab plan={saved.plan} />}
          {tab === "sitemap" && <SitemapTab sitemap={saved.plan.sitemap} />}
          {tab === "features" && <FeaturesTab features={saved.plan.features} options={options} />}
          {tab === "content" && <ContentTab plan={saved.plan} />}
          {tab === "seo" && <SeoTab planId={saved.id} items={saved.plan.seo_checklist} />}
          {tab === "examples" && <ExamplesTab businessType={saved.input.business_type} businessLabel={businessLabel} />}
        </div>
      </div>

      <RecentPlans excludeId={saved.id} className="mt-12" />

      <p className="mt-12 border-t border-line pt-5 text-sm text-muted" data-testid="plan-footer">
        Plan ID {saved.id}. Made with rule engine v{saved.engine_version} on {created}. Saved plans keep the rules they were
        made with.
      </p>
      {toast}
    </div>
  );
}

function PlanSkeleton() {
  return (
    <div className="container-page pt-8 sm:pt-12" aria-busy="true" aria-label="Loading the plan">
      <div className="grid animate-pulse grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <div className="h-4 w-32 rounded bg-line" />
          <div className="mt-3 h-12 w-2/3 rounded-lg bg-line" />
          <div className="mt-6 space-y-2.5">
            <div className="h-4 w-full max-w-xl rounded bg-line" />
            <div className="h-4 w-11/12 max-w-xl rounded bg-line" />
            <div className="h-4 w-3/4 max-w-lg rounded bg-line" />
          </div>
        </div>
        <div className="h-48 rounded-[18px] bg-white lg:col-span-4" />
      </div>
      <div className="mt-8 h-11 w-full max-w-lg animate-pulse rounded-xl bg-line/70" />
      <div className="mt-8 h-12 border-b border-line" />
      <div className="mt-7 h-64 animate-pulse rounded-[18px] bg-white" />
    </div>
  );
}

function NotFoundState() {
  return (
    <section className="container-page py-20 sm:py-28">
      <h1 className="text-4xl font-extrabold sm:text-5xl">Plan not found</h1>
      <p className="mt-4 max-w-[36rem] text-lg text-muted">
        This link doesn't point to a saved plan. Check the address, or make a new plan. It takes about three minutes.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <ButtonLink to="/planner">Start a new plan</ButtonLink>
        <ButtonLink to="/" variant="secondary">
          Back to home
        </ButtonLink>
      </div>
    </section>
  );
}

function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <section className="container-page py-20" role="alert">
      <h1 className="text-3xl font-bold">We couldn't load this plan</h1>
      <p className="mt-3 max-w-[36rem] text-muted">{message}</p>
      <Button className="mt-6" onClick={onRetry}>
        Try again
      </Button>
    </section>
  );
}
