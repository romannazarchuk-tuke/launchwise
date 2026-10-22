"""Full user journeys as a first-time visitor: every check runs in a brand-new browser context (empty storage).

Usage (from the repo root):
    uv run --with playwright python qa/journeys_e2e.py [BASE_URL] [OUT_DIR] [AXE_JS]

Creates 3 plans (stays under the 10/min rate limit). AXE_JS is the path to axe-core's axe.min.js
(npm i axe-core), used for an automated accessibility scan; skipped if the file is missing.
"""

import json
import re
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import Browser, Page, expect, sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("QA_BASE_URL", "http://localhost:5173")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "qa/screenshots")
AXE = Path(sys.argv[3] if len(sys.argv) > 3 else "/tmp/axe/node_modules/axe-core/axe.min.js")
CHROMIUM = os.environ.get("CHROMIUM_PATH") or None  # None = Playwright's own Chromium
DEMO = "l34kndqa5h"
results: dict = {"journeys": [], "a11y": {}, "perf": {}}

JOURNEYS = [
    # name, business, goal, audience, features, budget, timeline
    ("Glow Studio", "Beauty salon", "Get bookings", "Local", ["Photo gallery", "Customer reviews"], "Standard", "Within a month"),
    ("Paper & Thread", "Online store", "Sell online", "International", ["Online payments", "Newsletter signup"], "Advanced", "Flexible"),
    ("North Advisory", "Consulting / Agency", "Get leads / calls", "National", [], "Starter", "As soon as possible"),
]


def fresh(browser: Browser, width=1440, height=900, **kw) -> Page:
    context = browser.new_context(viewport={"width": width, "height": height}, accept_downloads=True, **kw)
    page = context.new_page()
    page.errors = []  # type: ignore[attr-defined]
    page.on("console", lambda m: page.errors.append(m.text) if m.type == "error" else None)  # type: ignore[attr-defined]
    page.on("pageerror", lambda e: page.errors.append(str(e)))  # type: ignore[attr-defined]
    return page


def pick(page: Page, name: str) -> None:
    page.locator("label").filter(has=page.get_by_label(name, exact=True)).click()


def h1(page: Page):
    return page.get_by_role("heading", level=1)


def journey(browser: Browser, name, business, goal, audience, features, budget, timeline) -> dict:
    page = fresh(browser)
    page.goto(f"{BASE}/planner")
    expect(h1(page)).to_have_text("What kind of business is it?")
    expect(page.get_by_role("region", name="Your recent plans")).to_have_count(0)  # first visit: no list
    pick(page, business)
    page.get_by_label("Business name").fill(name)
    page.get_by_role("button", name="Next").click()
    pick(page, goal)
    # Back keeps answers
    page.get_by_role("button", name="Back").click()
    expect(page.get_by_label(business, exact=True)).to_be_checked()
    expect(page.get_by_label("Business name")).to_have_value(name)
    page.get_by_role("button", name="Next").click()
    expect(page.get_by_label(goal, exact=True)).to_be_checked()
    page.get_by_role("button", name="Next").click()
    pick(page, audience)
    page.reload()  # reload mid-wizard
    expect(h1(page)).to_have_text("Who are your customers?")
    expect(page.get_by_label(audience, exact=True)).to_be_checked()
    page.get_by_role("button", name="Next").click()
    for f in features:
        pick(page, f)
    page.get_by_role("button", name="Next").click()
    pick(page, budget)
    pick(page, timeline)
    page.get_by_role("button", name="Review answers").click()
    # edit from the summary
    page.get_by_role("button", name="Edit main goal").click()
    expect(page.get_by_role("button", name="Back to summary")).to_be_visible()
    page.get_by_role("button", name="Back to summary").click()
    expect(h1(page)).to_have_text("Check your answers")
    page.get_by_role("button", name="Generate my plan").click()
    page.wait_for_url(re.compile(r"/plan/[a-z0-9]{10}$"), timeout=15000)
    plan_id = page.url.rsplit("/", 1)[1]
    data = page.request.get(f"{BASE}/api/plans/{plan_id}").json()["plan"]
    summary = {
        "id": plan_id, "business": business, "site_type": data["site_type"]["name"],
        "complexity": f'{data["complexity"]["score"]}/10 {data["complexity"]["label"]}',
        "launch": [p["name"] for p in data["sitemap"] if p["priority"] == "launch"],
        "later": [p["name"] for p in data["sitemap"] if p["priority"] == "later"],
        "must": [f["name"] for f in data["features"] if f["priority"] == "must"],
        "seo": len(data["seo_checklist"]),
    }
    # reload on a result tab
    page.get_by_role("tab", name="Sitemap").click()
    page.reload()
    expect(page.get_by_role("tab", name="Sitemap")).to_have_attribute("aria-selected", "true")
    assert not page.errors, page.errors  # type: ignore[attr-defined]
    page.context.close()
    return summary


def share_in_fresh_session(browser: Browser, plan_id: str) -> None:
    page = fresh(browser)
    page.context.grant_permissions(["clipboard-read", "clipboard-write"], origin=BASE)
    page.goto(f"{BASE}/plan/{plan_id}")
    page.get_by_role("button", name="Copy share link").click()
    expect(page.get_by_role("status")).to_have_text("Link copied")
    link = page.evaluate("navigator.clipboard.readText()")
    page.get_by_role("button", name="Copy brief").click()
    expect(page.get_by_role("status")).to_have_text("Copied!")  # the brief is fetched first, then copied
    brief = page.evaluate("navigator.clipboard.readText()")
    files = {}
    for fmt in ("md", "txt"):
        with page.expect_download() as info:
            page.get_by_role("link", name=f"Download .{fmt}").click()
        files[fmt] = info.value.suggested_filename
    page.context.close()
    # open the shared link as someone else: a new context, nothing stored
    other = fresh(browser)
    other.goto(link)
    expect(h1(other)).to_be_visible()
    title = h1(other).inner_text()
    other.context.close()
    assert brief.startswith("# Website plan") and files == {"md": f"launchwise-plan-{plan_id}.md", "txt": f"launchwise-plan-{plan_id}.txt"}
    print(f"  share link {link} opens in a fresh session ('{title}'); brief {len(brief)} chars; downloads {list(files.values())}")


def screenshots_and_checks(browser: Browser) -> None:
    pages = {"home": "/", "planner": "/planner", "result": f"/plan/{DEMO}"}
    for width, height in ((390, 844), (768, 1024), (1440, 900)):
        for name, path in pages.items():
            page = fresh(browser, width, height)
            t0 = time.time()
            page.goto(f"{BASE}{path}", wait_until="load")
            expect(h1(page)).to_be_visible()
            page.wait_for_load_state("networkidle")
            if width == 1440:
                timing = page.evaluate("""() => {
                  const nav = performance.getEntriesByType('navigation')[0];
                  const fcp = performance.getEntriesByName('first-contentful-paint')[0];
                  const bytes = performance.getEntriesByType('resource').reduce((s, r) => s + (r.transferSize || 0), nav.transferSize || 0);
                  return {ttfb: Math.round(nav.responseStart), dcl: Math.round(nav.domContentLoadedEventEnd),
                          load: Math.round(nav.loadEventEnd), fcp: fcp ? Math.round(fcp.startTime) : null, kb: Math.round(bytes / 1024)};
                }""")
                timing["wall_ms"] = round((time.time() - t0) * 1000)
                results["perf"][name] = timing
            overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            assert overflow <= 0, f"{name} @ {width}: horizontal scroll {overflow}px"
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / f"{name}-{width}.png"), full_page=True)
            if AXE.exists() and width in (390, 1440):
                page.add_script_tag(path=str(AXE))
                found = page.evaluate("""async () => {
                  const r = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice']}});
                  return r.violations.map(v => ({id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length,
                                                 sample: v.nodes.slice(0, 3).map(n => n.target.join(' '))}));
                }""")
                results["a11y"][f"{name}-{width}"] = found
            assert not page.errors, f"{name} @ {width}: {page.errors}"  # type: ignore[attr-defined]
            page.context.close()
    print("  9 screenshots (390/768/1440 x home/planner/result), no horizontal scroll, no console errors")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox", "--disable-dev-shm-usage"])
        print("== journeys (fresh session each)")
        for j in JOURNEYS:
            s = journey(browser, *j)
            results["journeys"].append(s)
            print(f"  {s['business']}: {s['site_type']}, {s['complexity']}, launch {s['launch']}, later {s['later']}")
        sites = {s["site_type"] for s in results["journeys"]}
        launches = {tuple(s["launch"]) for s in results["journeys"]}
        assert len(sites) == 3 and len(launches) == 3, "plans don't differ enough"
        print("== share / copy / download")
        share_in_fresh_session(browser, results["journeys"][0]["id"])
        print("== unknown plan id (fresh session)")
        page = fresh(browser)
        page.goto(f"{BASE}/plan/abcdefghij")
        expect(h1(page)).to_have_text("Plan not found")
        page.context.close()
        print("== responsive, performance, accessibility")
        screenshots_and_checks(browser)
        browser.close()
    (OUT / "journeys_e2e.json").write_text(json.dumps(results, indent=1))
    print("RESULTS:", json.dumps({"perf": results["perf"],
                                  "a11y": {k: [(v["id"], v["impact"], v["nodes"]) for v in vs] for k, vs in results["a11y"].items()}}))
    print("CREATED PLANS:", " ".join(s["id"] for s in results["journeys"]))


if __name__ == "__main__":
    main()
