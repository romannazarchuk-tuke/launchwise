"""Site-wide end-to-end checks (Playwright).

Usage (from the repo root):
    uv run --with playwright python qa/site_e2e.py [BASE_URL] [OUT_DIR]

Covers: page titles and one <h1> per route, no console errors, About/404 screenshots,
"Your recent plans" (create 2, reload, remove, clear all, missing plans dropped),
the site with browser storage blocked, and the friendly 429 message.
Creates 3 real plans; their ids are printed at the end so they can be cleaned up.
"""

import re
import os
import sys
from pathlib import Path

from playwright.sync_api import Browser, Page, expect, sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("QA_BASE_URL", "http://localhost:5173")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "qa/screenshots")
CHROMIUM = os.environ.get("CHROMIUM_PATH") or None  # None = Playwright's own Chromium
created: list[str] = []

ROUTES = {
    "/": "LaunchWise: plan your small business website in 3 minutes",
    "/planner": "Plan your website | LaunchWise",
    "/plan/l34kndqa5h": "Bean There website plan | LaunchWise",
    "/about": "About | LaunchWise",
    "/no-such-page": "Page not found | LaunchWise",
    "/plan/zzzzzzzzzz": "Plan not found | LaunchWise",
}


def shot(page: Page, name: str) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    page.mouse.move(0, 0)
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    print(f"  screenshot {OUT / name}.png")


def pick(page: Page, name: str) -> None:
    page.locator("label").filter(has=page.get_by_label(name, exact=True)).click()


def fill_wizard(page: Page, name: str, business: str = "Coffee shop") -> None:
    """Answer all five steps quickly and click Generate."""
    page.goto(f"{BASE}/planner")
    pick(page, business)
    page.get_by_label("Business name").fill(name)
    page.get_by_role("button", name="Next").click()
    pick(page, "Build brand awareness")
    page.get_by_role("button", name="Next").click()
    pick(page, "Local")
    page.get_by_role("button", name="Next").click()
    page.get_by_role("button", name="Next").click()
    pick(page, "Starter")
    pick(page, "Flexible")
    page.get_by_role("button", name="Review answers").click()
    page.get_by_role("button", name="Generate my plan").click()


def make_plan(page: Page, name: str, business: str = "Coffee shop") -> str:
    """Create a real plan through the wizard and return its id."""
    fill_wizard(page, name, business)
    page.wait_for_url(re.compile(r"/plan/[a-z0-9]{10}$"), timeout=15000)
    plan_id = page.url.rsplit("/", 1)[1]
    created.append(plan_id)
    return plan_id


def recent(page: Page):
    return page.get_by_role("region", name="Your recent plans")


def check_routes(browser: Browser, errors: list[str]) -> None:
    print("== titles, one h1, console")
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.on("console", lambda m: errors.append(f"{page.url}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"{page.url}: {e}"))
    for path, title in ROUTES.items():
        page.goto(f"{BASE}{path}")
        expect(page.get_by_role("heading", level=1)).to_be_visible()
        expect(page).to_have_title(title)
        assert page.locator("h1").count() == 1, f"{path}: more than one h1"
        print(f"  {path}: '{title}', 1 h1")
    page.close()


def check_about_404(browser: Browser) -> None:
    print("== about + 404 screenshots")
    for label, width, height in (("1440", 1440, 900), ("390", 390, 844)):
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"{BASE}/about")
        for heading in ("How LaunchWise works", "Project plan", "Privacy"):
            expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "about: horizontal scroll"
        shot(page, f"about-{label}")
        page.goto(f"{BASE}/no-such-page")
        expect(page.get_by_role("link", name="Build my website plan")).to_be_visible()
        expect(page.get_by_role("link", name="Back to home")).to_be_visible()
        shot(page, f"404-{label}")
        page.close()


def check_recent_plans(browser: Browser) -> None:
    print("== recent plans")
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(f"{BASE}/planner")
    page.evaluate("localStorage.clear(); sessionStorage.clear()")
    page.reload()
    expect(recent(page)).to_have_count(0)  # hidden while empty

    first = make_plan(page, "Recent One")
    second = make_plan(page, "Recent Two", business="Beauty salon")
    # the result page lists the other plan (not itself)
    expect(recent(page).get_by_role("link", name=re.compile("Recent One"))).to_be_visible()
    expect(recent(page).get_by_role("link", name=re.compile("Recent Two"))).to_have_count(0)

    page.goto(f"{BASE}/planner")
    links = recent(page).get_by_role("link")
    expect(links).to_have_count(2)
    expect(links.nth(0)).to_contain_text("Recent Two")  # newest first
    expect(links.nth(0)).to_contain_text("Booking website")
    page.reload()
    expect(recent(page).get_by_role("link")).to_have_count(2)
    print(f"  2 plans listed after reload ({second}, {first}), newest first")

    recent(page).get_by_role("button", name="Remove Recent One from recent plans").click()
    expect(recent(page).get_by_role("link")).to_have_count(1)
    page.reload()
    expect(recent(page).get_by_role("link")).to_have_count(1)
    recent(page).get_by_role("button", name="Clear all").click()
    expect(recent(page)).to_have_count(0)
    print("  remove one, clear all: OK (block hidden when empty)")

    # a stored plan that no longer exists is dropped quietly
    page.evaluate(
        """localStorage.setItem('launchwise.recent.v1', JSON.stringify([
            {id: 'zzzzzzzzzz', label: 'Deleted plan', siteType: 'Portfolio', createdAt: new Date().toISOString()},
            {id: '%s', label: 'Still here', siteType: 'Booking website', createdAt: new Date().toISOString()}]))"""
        % second
    )
    page.reload()
    expect(recent(page).get_by_role("link", name=re.compile("Still here"))).to_be_visible()
    expect(recent(page).get_by_role("link", name=re.compile("Deleted plan"))).to_have_count(0, timeout=8000)
    print("  missing plan (404) removed from the list quietly")
    page.evaluate("localStorage.clear()")
    page.close()


def check_storage_blocked(browser: Browser) -> None:
    print("== storage blocked")
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    context.add_init_script(
        """for (const name of ['localStorage', 'sessionStorage']) {
             Object.defineProperty(window, name, { get() { throw new DOMException('blocked', 'SecurityError'); } });
           }"""
    )
    page = context.new_page()
    page_errors: list[str] = []
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    plan_id = make_plan(page, "No Storage")
    expect(page.get_by_role("heading", level=1)).to_have_text("No Storage")
    page.get_by_role("tab", name="SEO checklist").click()
    page.get_by_role("tabpanel").get_by_role("checkbox").first.check()
    expect(page.get_by_test_id("seo-progress")).to_contain_text("1 of")
    page.goto(f"{BASE}/planner")
    expect(page.get_by_role("heading", level=1)).to_have_text("What kind of business is it?")
    assert not page_errors, page_errors
    print(f"  wizard, plan page and checklist work with storage blocked ({plan_id}); no page errors")
    context.close()


def check_rate_limit_message(browser: Browser) -> None:
    print("== 429 message (faked in the browser)")
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.route("**/api/plans", lambda route: route.fulfill(
        status=429, content_type="application/json",
        body='{"detail": "You\'re creating plans very quickly. Please wait a minute and try again."}'))
    page.goto(f"{BASE}/planner")
    page.evaluate("sessionStorage.clear()")
    fill_wizard(page, "Too Fast")
    alert = page.get_by_role("alert")
    expect(alert).to_contain_text("You're creating plans very quickly — please wait a minute and try again.")
    expect(alert).to_contain_text("Your answers are saved")
    expect(page.get_by_text('Coffee shop, "Too Fast"')).to_be_visible()
    print("  friendly 429 message shown, answers kept")
    page.close()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox", "--disable-dev-shm-usage"])
        check_routes(browser, errors)
        check_about_404(browser)
        check_recent_plans(browser)
        check_storage_blocked(browser)
        check_rate_limit_message(browser)
        browser.close()
    # the plan-not-found route deliberately triggers one 404 from the API
    unexpected = [e for e in errors if not re.search(r"Failed to load resource: .*status of 404", e)]
    if unexpected:
        raise SystemExit(f"Console errors: {unexpected}")
    print("console errors: 0 (besides the deliberate 404 on /plan/zzzzzzzzzz)")
    print("CREATED PLANS:", " ".join(created))
    print("ALL SITE CHECKS PASSED")


if __name__ == "__main__":
    main()
