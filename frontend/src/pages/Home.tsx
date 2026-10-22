import { Check, Coffee, Globe, Palette, Scissors, ShoppingBag } from "lucide-react";
import type { ReactNode } from "react";
import { AuthorityBadge } from "../components/AuthorityBadge";
import { ProgressRing } from "../components/ProgressRing";
import { ButtonLink } from "../components/ButtonLink";
import { SitemapPreview } from "../components/SitemapPreview";
import { useTitle } from "../lib/useTitle";
import { pageColor } from "../lib/pageColors";

export default function Home() {
  useTitle();
  return (
    <>
      <Hero />
      <HowItWorks />
      <WhatYouGet />
      <WhoItsFor />
      <FinalCta />
    </>
  );
}

// ---------- hero ----------

function Hero() {
  return (
    <section className="container-page grid grid-cols-1 items-center gap-10 pt-12 pb-16 sm:pt-16 lg:grid-cols-12 lg:gap-12 lg:pt-20 lg:pb-24">
      <div className="lg:col-span-5">
        <h1 className="text-[2.6rem] leading-[1.04] font-extrabold sm:text-[3.4rem] lg:text-[3.8rem]">
          Your next website starts with a plan.
        </h1>
        <p className="mt-6 max-w-[34rem] text-lg text-muted">
          Answer five quick questions about your business. In about three minutes you get a clear website brief: the
          pages you need, what goes on each one, and your first steps for Google.
        </p>
        <div className="mt-8 flex flex-wrap items-center gap-3">
          <ButtonLink to="/planner" size="lg">
            Build my website plan
          </ButtonLink>
          <ButtonLink to="/#how-it-works" size="lg" variant="secondary">
            See how it works
          </ButtonLink>
        </div>
        <p className="mt-5 text-sm text-muted">Free, no sign-up. Every plan gets its own link to share.</p>
      </div>
      <div className="lg:col-span-7">
        <SitemapPreview />
      </div>
    </section>
  );
}

// ---------- how it works ----------

const STEPS = [
  {
    title: "Tell us about your business",
    text: "Choose your business type, main goal, audience, the features you want and your budget. Five short steps, mostly clicks.",
  },
  {
    title: "Get your plan",
    text: "See the type of site that fits, every page with its sections, and the features that matter, each with a short reason why.",
  },
  {
    title: "Export the brief",
    text: "Copy it or download it as a Markdown or text file, then hand it to a web developer, an agency or an AI website builder.",
  },
];

function HowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-20 border-y border-line bg-white py-16 sm:py-20">
      <div className="container-page">
        <h2 className="text-3xl font-bold sm:text-[2.4rem]">How it works</h2>
        <ol className="mt-10 grid grid-cols-1 gap-8 md:grid-cols-3 md:gap-6">
          {STEPS.map((step, i) => (
            <li key={step.title} className="relative">
              {/* connector to the next step (desktop) */}
              {i < STEPS.length - 1 && (
                <span aria-hidden="true" className="absolute top-5 left-14 hidden h-px w-[calc(100%-3rem)] bg-line md:block" />
              )}
              <span className="relative flex size-10 items-center justify-center rounded-full bg-violet font-display text-lg font-bold text-white">
                {i + 1}
              </span>
              <h3 className="mt-4 text-xl font-semibold">{step.title}</h3>
              <p className="mt-2 max-w-[22rem] text-muted">{step.text}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

// ---------- what you get ----------

function Pill({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "violet" | "mint" }) {
  const tones = {
    neutral: "border border-line bg-white text-muted",
    violet: "bg-violet-50 text-violet-deep",
    mint: "bg-mint text-mint-ink",
  };
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${tones[tone]}`}>{children}</span>;
}

function PageChip({ pageKey, name, later = false }: { pageKey: string; name: string; later?: boolean }) {
  const c = pageColor(pageKey);
  return later ? (
    <span className="rounded-lg border border-dashed border-ink/25 bg-white px-2.5 py-1 text-xs font-medium text-muted">{name}</span>
  ) : (
    <span className={`rounded-lg px-2.5 py-1 text-xs font-semibold ${c.bg} ${c.ink}`}>{name}</span>
  );
}

function ScoreRing({ done, total }: { done: number; total: number }) {
  return (
    <span className="flex items-center gap-3">
      <ProgressRing value={done} max={total} />
      <span className="text-sm font-semibold text-ink">{done} of {total} done</span>
    </span>
  );
}

const OUTPUTS: { title: string; text: string; visual: ReactNode }[] = [
  {
    title: "Site type",
    text: "The kind of site you need, from a one-page landing page to an online store, and why it fits your goal.",
    visual: <Pill tone="violet">Booking website</Pill>,
  },
  {
    title: "Sitemap",
    text: "Every page, split into what to launch now and what can wait, with the sections each page needs.",
    visual: (
      <span className="flex flex-wrap gap-1.5">
        <PageChip pageKey="home" name="Home" />
        <PageChip pageKey="menu" name="Menu" />
        <PageChip pageKey="booking" name="Reserve a table" />
        <PageChip pageKey="events" name="Events" later />
      </span>
    ),
  },
  {
    title: "Features",
    text: "Must-haves and nice-to-haves, including useful ones you didn't think of.",
    visual: (
      <span className="flex w-full flex-col gap-2 text-sm">
        <span className="flex items-center justify-between gap-2">
          <span className="font-medium">Online booking</span>
          <Pill tone="mint">Must-have</Pill>
        </span>
        <span className="flex items-center justify-between gap-2">
          <span className="font-medium">Customer reviews</span>
          <Pill tone="violet">Recommended</Pill>
        </span>
      </span>
    ),
  },
  {
    title: "Content ideas",
    text: "Concrete ideas for what to write and show on each page, for your type of business.",
    visual: (
      <span className="flex items-start gap-2 text-sm text-ink">
        <Check className="mt-0.5 size-4 shrink-0 text-violet" aria-hidden="true" />
        Mark vegan, gluten-free and lactose-free options
      </span>
    ),
  },
  {
    title: "SEO checklist",
    text: "Your first steps for Google, from page titles to your Google Business Profile, with a progress tracker.",
    visual: <ScoreRing done={5} total={12} />,
  },
  {
    title: "Similar live sites",
    text: "Real websites from businesses like yours, so you can show your developer what you like.",
    visual: (
      <span className="flex flex-col items-start gap-2">
        <span className="flex items-center gap-2 text-sm font-medium">
          <Globe className="size-4 shrink-0 text-muted" aria-hidden="true" />
          Neighbourhood coffee shop
        </span>
        <AuthorityBadge dr={24} />
      </span>
    ),
  },
];

function WhatYouGet() {
  return (
    <section className="container-page py-16 sm:py-24">
      <h2 className="text-3xl font-bold sm:text-[2.4rem]">What's in your plan</h2>
      <p className="mt-3 max-w-[36rem] text-lg text-muted">The questions a developer asks in the first meeting, answered in advance.</p>
      <ul className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {OUTPUTS.map((item) => (
          <li key={item.title} className="flex flex-col rounded-[18px] border border-line bg-white p-5 shadow-soft">
            {/* a small real piece of the output, so the card shows instead of tells */}
            <div className="flex min-h-[4.5rem] items-center rounded-xl bg-paper px-4 py-3">{item.visual}</div>
            <h3 className="mt-5 text-xl font-semibold">{item.title}</h3>
            <p className="mt-2 text-muted">{item.text}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}

// ---------- who it's for ----------

const AUDIENCE = [
  { icon: Coffee, title: "Coffee shops", text: "Menu, opening hours and table bookings, set up for people searching “coffee near me”." },
  { icon: Scissors, title: "Beauty salons", text: "Treatments with prices, your team and online appointments." },
  { icon: ShoppingBag, title: "Online stores", text: "Shop, product pages, checkout and the shipping terms you're required to publish." },
  { icon: Palette, title: "Freelancers", text: "A portfolio that puts your best work first and makes it easy to hire you." },
];

function WhoItsFor() {
  return (
    <section className="border-y border-line bg-white py-16 sm:py-20">
      <div className="container-page">
        <h2 className="text-3xl font-bold sm:text-[2.4rem]">Made for small businesses</h2>
        <p className="mt-3 max-w-[36rem] text-lg text-muted">
          And for anyone who needs a website but doesn't know where to start.
        </p>
        <ul className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {AUDIENCE.map(({ icon: Icon, title, text }) => (
            <li key={title} className="rounded-[18px] border border-line bg-paper p-5">
              <span className="flex size-11 items-center justify-center rounded-xl bg-violet-50 text-violet-deep">
                <Icon className="size-5" aria-hidden="true" />
              </span>
              <h3 className="mt-4 text-lg font-semibold">{title}</h3>
              <p className="mt-1.5 text-[0.95rem] text-muted">{text}</p>
            </li>
          ))}
        </ul>
        <p className="mt-6 text-muted">Also for restaurants, local services and consultants.</p>
      </div>
    </section>
  );
}

// ---------- final CTA ----------

function FinalCta() {
  return (
    <section className="container-page pt-16 sm:pt-20">
      <div className="rounded-[28px] bg-violet px-6 py-12 text-white sm:px-12 sm:py-14">
        <h2 className="max-w-[30rem] text-3xl font-bold text-white sm:text-[2.4rem]">Ready to see what your website needs?</h2>
        <p className="mt-3 max-w-[32rem] text-lg text-white">It takes about three minutes, and you don't need an account.</p>
        <ButtonLink to="/planner" size="lg" variant="inverse" className="mt-8">
          Build my website plan
        </ButtonLink>
      </div>
    </section>
  );
}
