import type { FeatureItem, Options } from "../../api";
import { OptionIcon } from "../../lib/icons";

const GROUPS = [
  { priority: "must", title: "Must-have", text: "Plan these into the first version of the site." },
  { priority: "nice", title: "Nice to have", text: "Useful, but they can wait until the site is live." },
] as const;

export function FeaturesTab({ features, options }: { features: FeatureItem[]; options: Options | null }) {
  const iconOf = (id: string) => options?.features.find((f) => f.id === id)?.icon;
  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-2 lg:gap-6">
      {GROUPS.map((group) => {
        const items = features.filter((f) => f.priority === group.priority);
        return (
          <section key={group.priority}>
            <h2 className="text-xl font-semibold">{group.title}</h2>
            <p className="mt-1 text-muted">{group.text}</p>
            {items.length === 0 ? (
              <p className="mt-4 rounded-[18px] border border-dashed border-ink/20 p-5 text-muted">Nothing here for your plan.</p>
            ) : (
              <ul className="mt-4 space-y-3">
                {items.map((f) => (
                  <li key={f.id} className="flex gap-3 rounded-[18px] border border-line bg-white p-4 shadow-soft">
                    <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-deep">
                      <OptionIcon name={iconOf(f.id)} />
                    </span>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-semibold">{f.name}</h3>
                        {f.recommended && (
                          <span className="rounded-full bg-violet-50 px-2.5 py-0.5 text-xs font-semibold text-violet-deep">
                            Recommended for you
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-[0.95rem] text-muted">{f.why}</p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        );
      })}
    </div>
  );
}
