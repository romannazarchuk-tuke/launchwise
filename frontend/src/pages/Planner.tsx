import { ArrowLeft, LoaderCircle, RotateCcw } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router";
import { api, ApiError, type Options } from "../api";
import { Button } from "../components/ButtonLink";
import { LanguageChips } from "../components/planner/LanguageChips";
import { OptionCards } from "../components/planner/OptionCards";
import { ProgressSteps } from "../components/planner/ProgressSteps";
import { Summary } from "../components/planner/Summary";
import { RecentPlans } from "../components/RecentPlans";
import { addRecentPlan } from "../lib/recentPlans";
import {
  type Answers,
  clearProgress,
  EMPTY_ANSWERS,
  firstIncompleteStep,
  loadProgress,
  REVIEW_STEP,
  sanitize,
  saveProgress,
  stepProblem,
  STEPS,
  toPlanInput,
} from "../lib/plannerState";
import { useTitle } from "../lib/useTitle";

const QUESTIONS = [
  { title: "What kind of business is it?", hint: "Pick the closest match. You can add your business name too." },
  { title: "What should the website do for you first?", hint: "Pick the one that matters most right now. The plan is built around it." },
  { title: "Who are your customers?", hint: "This decides how much the plan focuses on local search, languages and reach." },
  { title: "Which features do you want?", hint: "Not sure? You can skip — we'll recommend some." },
  { title: "What's your budget and timeline?", hint: "Your budget decides how many pages go live first. The rest goes on a “later” list." },
  { title: "Check your answers", hint: "Change anything you like, then generate your plan." },
];

type LoadState = { status: "loading" } | { status: "error"; message: string } | { status: "ready"; options: Options };

export default function Planner() {
  useTitle("Plan your website");
  const navigate = useNavigate();

  const [load, setLoad] = useState<LoadState>({ status: "loading" });
  const [answers, setAnswers] = useState<Answers>(EMPTY_ANSWERS);
  const [step, setStep] = useState(0);
  const [returnToReview, setReturnToReview] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<ApiError | null>(null);

  const headingRef = useRef<HTMLHeadingElement>(null);
  const moved = useRef(false); // focus the heading only after the user moves between steps

  // ----- load the choices, then restore saved progress -----
  const loadOptions = useCallback(() => {
    setLoad({ status: "loading" });
    api
      .getOptions()
      .then((options) => {
        const saved = loadProgress();
        if (saved) {
          const restored = sanitize(saved.answers, options);
          setAnswers(restored);
          // never restore past the first unanswered step
          setStep(Math.min(saved.step, firstIncompleteStep(restored, options.limits)));
        }
        setLoad({ status: "ready", options });
      })
      .catch((err: unknown) => {
        setLoad({ status: "error", message: err instanceof ApiError ? err.message : "Couldn't load the questions." });
      });
  }, []);

  useEffect(loadOptions, [loadOptions]);

  // ----- persist every change -----
  useEffect(() => {
    if (load.status === "ready" && !submitting) saveProgress(answers, step);
  }, [answers, step, load.status, submitting]);

  // ----- move focus to the new question for keyboard and screen-reader users -----
  useEffect(() => {
    if (!moved.current) return;
    window.scrollTo({ top: 0 });
    headingRef.current?.focus({ preventScroll: true });
  }, [step]);

  if (load.status === "loading") return <PlannerSkeleton />;
  if (load.status === "error") return <LoadError message={load.message} onRetry={loadOptions} />;

  const { options } = load;
  const limits = options.limits;
  const problem = step < REVIEW_STEP ? stepProblem(step, answers, limits) : null;
  const reachable = firstIncompleteStep(answers, limits);

  const update = <K extends keyof Answers>(key: K, value: Answers[K]) => {
    setAnswers((a) => ({ ...a, [key]: value }));
    setSubmitError(null);
  };

  function go(next: number) {
    moved.current = true;
    setStep(next);
  }

  function next() {
    if (problem) return;
    if (returnToReview || step === STEPS.length - 1) {
      setReturnToReview(false);
      go(firstIncompleteStep(answers, limits)); // the review screen, unless something is still missing
    } else {
      go(step + 1);
    }
  }

  function editFromReview(target: number) {
    setReturnToReview(true);
    go(target);
  }

  function startOver() {
    clearProgress();
    setAnswers(EMPTY_ANSWERS);
    setReturnToReview(false);
    setSubmitError(null);
    go(0);
  }

  async function submit() {
    setSubmitting(true);
    setSubmitError(null);
    try {
      const created = await api.createPlan(toPlanInput(answers));
      clearProgress(); // the plan is saved on the server; the next visit to /planner starts fresh
      addRecentPlan({
        id: created.id,
        label: answers.business_name.trim() || options.business_types.find((b) => b.id === answers.business_type)?.label || "Website plan",
        siteType: created.plan.site_type.name,
        createdAt: new Date().toISOString(),
      });
      navigate(`/plan/${created.id}`);
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err : new ApiError(0, "Something went wrong. Please try again."));
      setSubmitting(false);
    }
  }

  const question = QUESTIONS[step];
  const onReview = step === REVIEW_STEP;

  return (
    <section className="container-page max-w-[60rem] py-8 sm:py-12">
      {step === 0 && <RecentPlans className="mb-8" />}
      <ProgressSteps step={step} reachable={reachable} onGo={go} />

      <div className="mt-6 rounded-[28px] border border-line bg-white p-5 shadow-soft sm:p-8">
        <p className="text-sm font-medium text-muted">{onReview ? "All five steps done" : `Step ${step + 1} of ${STEPS.length}`}</p>
        <h1 ref={headingRef} tabIndex={-1} className="mt-1 text-[1.9rem] leading-tight font-bold outline-none sm:text-[2.3rem]">
          {question.title}
        </h1>
        <p className="mt-2 max-w-[40rem] text-muted">{question.hint}</p>

        <div className="mt-7 space-y-8">
          {step === 0 && (
            <>
              <OptionCards
                legend="Business type"
                hideLegend
                name="business_type"
                choices={options.business_types}
                value={answers.business_type}
                onChange={(id) => update("business_type", id)}
              />
              <div>
                <label htmlFor="business-name" className="font-display text-lg font-semibold">
                  Business name <span className="font-sans text-base font-normal text-muted">(optional)</span>
                </label>
                <p id="business-name-hint" className="text-[0.95rem] text-muted">We'll use it in your plan.</p>
                <input
                  id="business-name"
                  type="text"
                  autoComplete="organization"
                  maxLength={limits.business_name_max}
                  value={answers.business_name}
                  onChange={(e) => update("business_name", e.target.value)}
                  aria-describedby="business-name-hint"
                  placeholder="e.g. Bean There"
                  className="mt-2 h-12 w-full max-w-md rounded-xl border border-control bg-white px-4 text-base text-ink placeholder:text-muted focus:border-violet"
                />
              </div>
            </>
          )}

          {step === 1 && (
            <OptionCards
              legend="Main goal"
              hideLegend
              name="goal"
              choices={options.goals}
              value={answers.goal}
              onChange={(id) => update("goal", id)}
            />
          )}

          {step === 2 && (
            <>
              <OptionCards
                legend="Where are your customers?"
                name="audience"
                choices={options.audiences}
                value={answers.audience}
                onChange={(id) => update("audience", id)}
              />
              <LanguageChips
                choices={options.languages}
                value={answers.languages}
                max={limits.languages_max}
                onChange={(ids) => update("languages", ids)}
              />
            </>
          )}

          {step === 3 && (
            <OptionCards
              legend="Features"
              hideLegend
              name="features"
              multiple
              compact
              choices={options.features}
              value={answers.features}
              onChange={(ids) => update("features", ids)}
            />
          )}

          {step === 4 && (
            <>
              <OptionCards
                legend="Budget"
                name="budget"
                choices={options.budgets}
                value={answers.budget}
                onChange={(id) => update("budget", id)}
              />
              <OptionCards
                legend="Timeline"
                name="timeline"
                choices={options.timelines}
                value={answers.timeline}
                onChange={(id) => update("timeline", id)}
              />
            </>
          )}

          {onReview && <Summary answers={answers} options={options} onEdit={editFromReview} />}
        </div>

        {submitError && <SubmitError error={submitError} />}

        {/* navigation */}
        <div className="mt-8 flex flex-col-reverse gap-3 border-t border-line pt-6 sm:flex-row sm:items-center sm:justify-between">
          {step > 0 ? (
            <Button variant="secondary" onClick={() => go(step - 1)} disabled={submitting}>
              <ArrowLeft className="size-4" aria-hidden="true" />
              Back
            </Button>
          ) : (
            <span className="hidden sm:block" />
          )}

          <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-center sm:gap-4">
            {problem && (
              <p id="next-hint" className="text-sm text-muted sm:text-right" aria-live="polite">
                {problem}
              </p>
            )}
            {onReview ? (
              <Button size="lg" onClick={submit} disabled={submitting} aria-live="polite">
                {submitting ? (
                  <>
                    <LoaderCircle className="size-5 animate-spin" aria-hidden="true" />
                    Building your plan…
                  </>
                ) : (
                  "Generate my plan"
                )}
              </Button>
            ) : (
              <Button size="lg" onClick={next} disabled={!!problem} aria-describedby={problem ? "next-hint" : undefined}>
                {returnToReview ? "Back to summary" : step === STEPS.length - 1 ? "Review answers" : "Next"}
              </Button>
            )}
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={startOver}
        className="mt-5 inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-sm font-medium text-muted hover:text-violet-deep"
      >
        <RotateCcw className="size-3.5" aria-hidden="true" />
        Start over
      </button>
    </section>
  );
}

function SubmitError({ error }: { error: ApiError }) {
  return (
    <div role="alert" className="mt-6 rounded-xl border border-peach-ink/30 bg-peach px-4 py-3 text-peach-ink">
      <p className="font-semibold">We couldn't build your plan.</p>
      <p className="mt-0.5 text-[0.95rem]">
        {error.status === 429
          ? "You're creating plans very quickly — please wait a minute and try again."
          : error.message}{" "}
        Your answers are saved, so you can try again.
      </p>
      {error.fieldErrors.length > 0 && (
        <ul className="mt-1 list-disc pl-5 text-[0.95rem]">
          {error.fieldErrors.map((f) => (
            <li key={f.field + f.message}>
              {f.field}: {f.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function PlannerSkeleton() {
  return (
    <section className="container-page max-w-[60rem] py-8 sm:py-12" aria-busy="true" aria-label="Loading the planner">
      <div className="grid grid-cols-5 gap-2">
        {STEPS.map((s) => (
          <span key={s} className="h-1.5 rounded-full bg-line" />
        ))}
      </div>
      <div className="mt-6 animate-pulse rounded-[28px] border border-line bg-white p-5 shadow-soft sm:p-8">
        <div className="h-4 w-24 rounded bg-line" />
        <div className="mt-3 h-9 w-3/4 max-w-md rounded-lg bg-line" />
        <div className="mt-3 h-4 w-2/3 max-w-sm rounded bg-line" />
        <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }, (_, i) => (
            <div key={i} className="h-[5.5rem] rounded-[18px] bg-paper" />
          ))}
        </div>
      </div>
    </section>
  );
}

function LoadError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <section className="container-page max-w-[60rem] py-16">
      <div role="alert" className="rounded-[28px] border border-line bg-white p-8 shadow-soft">
        <h1 className="text-2xl font-bold">The planner couldn't load</h1>
        <p className="mt-2 max-w-[36rem] text-muted">{message}</p>
        <Button className="mt-6" onClick={onRetry}>
          Try again
        </Button>
      </div>
    </section>
  );
}
