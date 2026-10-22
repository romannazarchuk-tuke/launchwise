import { ExternalLink } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { api, type BusinessType, type ExampleSite } from "../../api";
import { AuthorityBadge } from "../AuthorityBadge";
import { Button } from "../ButtonLink";

type State = { status: "loading" } | { status: "done"; items: ExampleSite[] };

// Remember results while the page is open, so switching tabs doesn't refetch.
const cache = new Map<BusinessType, ExampleSite[]>();

export function ExamplesTab({ businessType, businessLabel }: { businessType: BusinessType; businessLabel: string }) {
  const [state, setState] = useState<State>(() =>
    cache.has(businessType) ? { status: "done", items: cache.get(businessType)! } : { status: "loading" },
  );

  const load = useCallback(() => {
    setState({ status: "loading" });
    api
      .getExamples(businessType)
      .then((res) => {
        if (res.items.length) cache.set(businessType, res.items);
        setState({ status: "done", items: res.items });
      })
      .catch(() => setState({ status: "done", items: [] })); // same friendly empty state
  }, [businessType]);

  useEffect(() => {
    if (!cache.has(businessType)) load();
  }, [businessType, load]);

  return (
    <div>
      <p className="max-w-[42rem] text-muted">
        Live sites from businesses like yours ({businessLabel.toLowerCase()}), found by FreeSerp. Use them for inspiration;
        we don't vet them.
      </p>

      {state.status === "loading" && (
        <ul className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3" aria-busy="true" aria-label="Loading example sites">
          {[0, 1, 2].map((i) => (
            <li key={i} className="h-44 animate-pulse rounded-[18px] border border-line bg-white" />
          ))}
        </ul>
      )}

      {state.status === "done" && state.items.length === 0 && (
        <div className="mt-5 rounded-[18px] border border-dashed border-ink/20 p-6">
          <h2 className="text-lg font-semibold">No example sites right now</h2>
          <p className="mt-1 max-w-[36rem] text-muted">
            FreeSerp didn't return any for this business type. Your plan is complete without them.
          </p>
          <Button variant="secondary" className="mt-4" onClick={load}>
            Try again
          </Button>
        </div>
      )}

      {state.status === "done" && state.items.length > 0 && (
        <ul className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {state.items.map((site) => (
            <li key={site.domain} className="flex flex-col rounded-[18px] border border-line bg-white p-5 shadow-soft">
              <h2 className="text-lg leading-snug font-semibold">
                <a
                  href={site.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded hover:text-violet-deep hover:underline hover:underline-offset-4"
                >
                  {site.title}
                  <ExternalLink className="ml-1.5 inline size-4 align-[-2px] text-muted" aria-hidden="true" />
                  <span className="sr-only"> (opens in a new tab)</span>
                </a>
              </h2>
              <p className="mt-1 text-sm text-muted">{site.domain}</p>
              {site.summary && <p className="mt-3 flex-1 text-[0.95rem] text-ink/80">{site.summary}</p>}
              <div className="mt-4">
                <AuthorityBadge dr={site.dr} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
