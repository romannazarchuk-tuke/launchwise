/**
 * "Your recent plans": a short list kept only in this browser (no accounts).
 * Every storage access is wrapped, so the site works when storage is blocked.
 */
import { useEffect, useState } from "react";

export interface RecentPlan {
  id: string;
  label: string; // business name, or the business type
  siteType: string; // e.g. "Booking website"
  createdAt: string; // ISO date
}

const KEY = "launchwise.recent.v1";
const MAX = 10;
const EVENT = "launchwise:recent-plans"; // lets every list on the page refresh after a change

function read(): RecentPlan[] {
  try {
    const data = JSON.parse(localStorage.getItem(KEY) ?? "[]");
    if (!Array.isArray(data)) return [];
    return data
      .filter(
        (p): p is RecentPlan =>
          p && typeof p.id === "string" && /^[a-z0-9]{10}$/.test(p.id) && typeof p.label === "string" &&
          typeof p.siteType === "string" && typeof p.createdAt === "string",
      )
      .slice(0, MAX);
  } catch {
    return [];
  }
}

function write(plans: RecentPlan[]) {
  try {
    if (plans.length) localStorage.setItem(KEY, JSON.stringify(plans.slice(0, MAX)));
    else localStorage.removeItem(KEY);
  } catch {
    // storage blocked or full: the list just isn't remembered
  }
  window.dispatchEvent(new Event(EVENT));
}

export function addRecentPlan(plan: RecentPlan) {
  write([plan, ...read().filter((p) => p.id !== plan.id)]); // newest first, no duplicates
}

export function removeRecentPlan(id: string) {
  const plans = read();
  if (plans.some((p) => p.id === id)) write(plans.filter((p) => p.id !== id));
}

export function clearRecentPlans() {
  write([]);
}

/** The current list, kept in sync with changes on this page and in other tabs. */
export function useRecentPlans(): RecentPlan[] {
  const [plans, setPlans] = useState<RecentPlan[]>(read);
  useEffect(() => {
    const refresh = () => setPlans(read());
    window.addEventListener(EVENT, refresh);
    window.addEventListener("storage", refresh); // other tabs
    return () => {
      window.removeEventListener(EVENT, refresh);
      window.removeEventListener("storage", refresh);
    };
  }, []);
  return plans;
}
