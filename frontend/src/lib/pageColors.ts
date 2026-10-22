/**
 * Colour of a sitemap page card, by the rule engine's stable page `key`.
 * Groups: home, what you offer, what visitors do, why trust you, content, legal/required.
 */

export type PageColor = { bg: string; ink: string; border: string };

const GROUPS = {
  home: { bg: "bg-lilac", ink: "text-lilac-ink", border: "border-lilac-ink/25" },
  offer: { bg: "bg-sky", ink: "text-sky-ink", border: "border-sky-ink/20" },
  action: { bg: "bg-mint", ink: "text-mint-ink", border: "border-mint-ink/20" },
  trust: { bg: "bg-peach", ink: "text-peach-ink", border: "border-peach-ink/20" },
  content: { bg: "bg-butter", ink: "text-butter-ink", border: "border-butter-ink/20" },
  legal: { bg: "bg-stone", ink: "text-stone-ink", border: "border-stone-ink/20" },
} satisfies Record<string, PageColor>;

const GROUP_BY_KEY: Record<string, keyof typeof GROUPS> = {
  home: "home",
  menu: "offer", shop: "offer", product: "offer", services: "offer",
  "services-prices": "offer", "services-rates": "offer", work: "offer",
  booking: "action", cart: "action", contact: "action", visit: "action", "service-area": "action",
  about: "trust", "our-story": "trust", team: "trust", "case-studies": "trust", "private-events": "trust",
  blog: "content", gallery: "content", events: "content", faq: "content",
  legal: "legal", shipping: "legal",
};

export function pageColor(key: string): PageColor {
  return GROUPS[GROUP_BY_KEY[key] ?? "legal"];
}
