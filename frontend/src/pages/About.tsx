import { ArrowDown, ArrowRight, Database, Globe, Monitor, Server, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import { ButtonLink } from "../components/ButtonLink";
import { pageColor } from "../lib/pageColors";
import { useTitle } from "../lib/useTitle";

export default function About() {
  useTitle("About");
  return (
    <div className="container-page pt-12 pb-4 sm:pt-16">
      <header className="max-w-[46rem]">
        <h1 className="text-[2.6rem] leading-[1.05] font-extrabold sm:text-[3.4rem]">About LaunchWise</h1>
        <p className="mt-5 text-lg text-muted">
          LaunchWise turns a few answers about your business into a clear website plan. Here's how it works, what it was
          built for, and what happens with your data.
        </p>
        <nav aria-label="On this page" className="mt-6 flex flex-wrap gap-2">
          {[
            ["#how-it-works", "How it works"],
            ["#project-plan", "Project plan"],
            ["#privacy", "Privacy"],
          ].map(([href, label]) => (
            <a
              key={href}
              href={href}
              className="rounded-full border border-line bg-white px-3.5 py-1.5 text-sm font-semibold text-muted hover:border-violet/40 hover:text-violet-deep"
            >
              {label}
            </a>
          ))}
        </nav>
      </header>

      <HowItWorks />
      <ProjectPlan />
      <Privacy />
    </div>
  );
}

/** Section with the heading in a narrow left column on wide screens. */
function Section({ id, title, intro, children }: { id: string; title: string; intro?: string; children: ReactNode }) {
  return (
    <section id={id} aria-labelledby={`${id}-heading`} className="scroll-mt-24 border-t border-line py-14 sm:py-16 lg:grid lg:grid-cols-12 lg:gap-10">
      <div className="lg:col-span-4">
        <h2 id={`${id}-heading`} className="text-3xl font-bold sm:text-[2.2rem] lg:sticky lg:top-24">
          {title}
        </h2>
        {intro && <p className="mt-3 max-w-[30rem] text-muted lg:sticky lg:top-40">{intro}</p>}
      </div>
      <div className="mt-8 lg:col-span-8 lg:mt-0">{children}</div>
    </section>
  );
}

// ---------- how it works ----------

const FLOW = [
  { title: "Your answers", text: "Business type, goal, audience, features and budget. Five short steps." },
  { title: "Written rules", text: "Fixed rules turn the answers into a site type, pages, features and an SEO checklist. Every decision comes with a reason." },
  { title: "Your plan", text: "Saved under its own link, ready to copy or download as a brief." },
];

const RULES = [
  { when: "Your goal is Get bookings", then: "Online booking becomes a must-have, with its own booking page." },
  { when: "Your customers are local", then: "Map & opening hours becomes a must-have, and the SEO checklist adds your Google Business Profile." },
  { when: "Your budget is Starter", then: "4 pages go live first, plus the required Privacy & imprint. The rest go on the Later list." },
  { when: "You run an online store", then: "Shipping & returns and Privacy & imprint are always part of the launch." },
];

const WHY_RULES = [
  { title: "Predictable", text: "The same answers always give the same plan, and every item tells you why it's there." },
  { title: "Instant", text: "Your plan is ready the moment you finish the last step." },
  { title: "Free", text: "No account, no payment, no usage costs behind the scenes." },
];

function HowItWorks() {
  return (
    <Section id="how-it-works" title="How LaunchWise works" intro="No AI model writes your plan. Written rules do, and you can read them.">
      <ol className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto_1fr_auto_1fr] md:items-stretch">
        {FLOW.map((step, i) => (
          <li key={step.title} className="contents">
            <div className="rounded-[18px] border border-line bg-white p-5 shadow-soft">
              <span className="flex size-8 items-center justify-center rounded-full bg-violet font-display text-sm font-bold text-white">
                {i + 1}
              </span>
              <h3 className="mt-3 text-lg font-semibold">{step.title}</h3>
              <p className="mt-1 text-[0.95rem] text-muted">{step.text}</p>
            </div>
            {i < FLOW.length - 1 && (
              <span className="flex items-center justify-center text-violet" aria-hidden="true">
                <ArrowRight className="hidden size-5 md:block" />
                <ArrowDown className="size-5 md:hidden" />
              </span>
            )}
          </li>
        ))}
      </ol>

      <h3 className="mt-10 text-xl font-semibold">A few of the rules</h3>
      <ul className="mt-4 overflow-hidden rounded-[18px] border border-line bg-white">
        {RULES.map((rule) => (
          <li key={rule.when} className="grid grid-cols-1 gap-1 border-b border-line px-5 py-4 last:border-b-0 sm:grid-cols-[13rem_1fr] sm:gap-6">
            <span className="font-semibold text-violet-deep">{rule.when}</span>
            <span className="text-ink/85">{rule.then}</span>
          </li>
        ))}
      </ul>

      <h3 className="mt-10 text-xl font-semibold">Why rules instead of an AI model</h3>
      <ul className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        {WHY_RULES.map((item) => (
          <li key={item.title} className="rounded-[18px] bg-violet-50 p-5">
            <p className="font-display text-lg font-semibold text-violet-deep">{item.title}</p>
            <p className="mt-1 text-[0.95rem] text-ink/80">{item.text}</p>
          </li>
        ))}
      </ul>

      <h3 className="mt-10 text-xl font-semibold">Real examples from FreeSerp</h3>
      <p className="mt-2 max-w-[40rem] text-ink/85">
        The Examples tab shows live websites from businesses like yours. They come from{" "}
        <a href="https://freeserp.ai" className="font-semibold text-violet-deep underline underline-offset-4">
          FreeSerp
        </a>
        , a free search index of live sites, filtered to leave out directories and unsuitable sites. They're there for
        inspiration, not as recommendations.
      </p>
    </Section>
  );
}

// ---------- project plan ----------

const AUDIENCE = [
  "Small business owners opening a coffee shop, beauty salon, online store or local service",
  "Freelancers and consultants who need a first portfolio or service site",
  "First-time founders who don't know where to start or how much a site involves",
];

const PAGES = [
  { path: "/", key: "home", name: "Home", text: "What LaunchWise does, how it works and an example plan." },
  { path: "/planner", key: "booking", name: "Planner", text: "Five short steps with progress and validation." },
  { path: "/plan/:id", key: "menu", name: "Your plan", text: "Overview, sitemap, features, content, SEO checklist and examples, under a shareable link." },
  { path: "/about", key: "about", name: "About", text: "How the recommendations work, and this project plan." },
];

const PLAN_CONTENTS = [
  "Site type and complexity",
  "Sitemap: what launches now, what can wait",
  "Features with a reason for each",
  "Content ideas per page",
  "SEO starter checklist with progress",
  "Similar live sites",
  "Export as Markdown or text",
];

function TechNode({ icon, title, text }: { icon: ReactNode; title: string; text: string }) {
  return (
    <div className="flex gap-3 rounded-[14px] border border-line bg-white p-4">
      <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-violet-50 text-violet-deep">{icon}</span>
      <div>
        <p className="font-semibold">{title}</p>
        <p className="text-sm text-muted">{text}</p>
      </div>
    </div>
  );
}

function ProjectPlan() {
  return (
    <Section id="project-plan" title="Project plan" intro="The plan this site was built from, step by step.">
      <h3 className="text-xl font-semibold">Goal</h3>
      <p className="mt-2 max-w-[42rem] text-ink/85">
        Help small business owners figure out what website they actually need (the type of site, pages, features,
        content and first SEO steps) in about three minutes, and leave with a clear brief they can hand to a web
        developer or an AI tool.
      </p>

      <h3 className="mt-10 text-xl font-semibold">Who it's for</h3>
      <ul className="mt-3 space-y-2">
        {AUDIENCE.map((item) => (
          <li key={item} className="flex gap-2.5 text-ink/85">
            <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-violet" aria-hidden="true" />
            {item}
          </li>
        ))}
      </ul>
      <blockquote className="mt-5 max-w-[40rem] rounded-[18px] border-l-4 border-violet bg-white px-5 py-4 font-display text-lg leading-snug text-ink">
        “I know I need a website, but I don't know what kind, which pages, or what to ask a developer.”
      </blockquote>

      <h3 className="mt-10 text-xl font-semibold">Pages</h3>
      <ul className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {PAGES.map((page) => {
          const color = pageColor(page.key);
          return (
            <li key={page.path} className={`rounded-[18px] border p-4 ${color.bg} ${color.border}`}>
              <p className={`font-display text-lg font-semibold ${color.ink}`}>{page.name}</p>
              <p className="text-sm text-muted">{page.path}</p>
              <p className="mt-2 text-[0.95rem] text-ink/80">{page.text}</p>
            </li>
          );
        })}
      </ul>

      <h3 className="mt-10 text-xl font-semibold">What a plan contains</h3>
      <ul className="mt-3 flex flex-wrap gap-2">
        {PLAN_CONTENTS.map((item) => (
          <li key={item} className="rounded-full border border-line bg-white px-3 py-1.5 text-[0.95rem]">
            {item}
          </li>
        ))}
      </ul>

      <h3 className="mt-10 text-xl font-semibold">Technical structure</h3>
      <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
        <TechNode icon={<Monitor className="size-5" aria-hidden="true" />} title="Browser" text="React, TypeScript, Vite and Tailwind, built to static files." />
        <TechNode icon={<ShieldCheck className="size-5" aria-hidden="true" />} title="nginx" text="Serves the site, sends /api to the backend, limits how fast plans can be created." />
        <TechNode icon={<Server className="size-5" aria-hidden="true" />} title="FastAPI" text="Checks every answer with Pydantic and runs the rule engine." />
        <TechNode icon={<Database className="size-5" aria-hidden="true" />} title="MariaDB" text="Stores each plan with the rule-engine version that made it." />
        <TechNode icon={<Globe className="size-5" aria-hidden="true" />} title="FreeSerp" text="Example sites, cached for an hour. If it's down, the plan still works." />
      </div>
      <p className="mt-4 text-sm text-muted">Out of scope: accounts, payments, AI-written text and an admin panel.</p>
    </Section>
  );
}

// ---------- privacy ----------

const PRIVACY = [
  "No accounts and no personal data needed. The business name is optional.",
  "Each plan is private to whoever has its link. There's no public list of plans, and plan pages ask search engines not to index them.",
  "Your recent plans and SEO checklist ticks are stored only in your browser. Clearing your browser data removes them.",
  "To prevent abuse, the server limits how many plans one IP address can create per minute. IP addresses are not saved with plans; the web server keeps standard technical logs.",
];

function Privacy() {
  return (
    <Section id="privacy" title="Privacy" intro="Short version: we don't want your data.">
      <ul className="space-y-3">
        {PRIVACY.map((item) => (
          <li key={item} className="flex gap-3 rounded-[14px] border border-line bg-white p-4 text-ink/85">
            <ShieldCheck className="mt-0.5 size-5 shrink-0 text-mint-ink" aria-hidden="true" />
            {item}
          </li>
        ))}
      </ul>
      <ButtonLink to="/planner" size="lg" className="mt-8">
        Build my website plan
      </ButtonLink>
    </Section>
  );
}
