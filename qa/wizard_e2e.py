"""End-to-end run of the /planner wizard in a real browser (Playwright).

Usage (from the repo root):
    uv run --with playwright python qa/wizard_e2e.py [BASE_URL] [OUT_DIR]

Checks the wizard rules on the way and saves screenshots of steps 1, 3, 4 and the summary
at 1440 px and 390 px. Exits non-zero on the first failed check.
"""

import re
import os
import sys
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("QA_BASE_URL", "http://localhost:5173")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "qa/screenshots")
CHROMIUM = os.environ.get("CHROMIUM_PATH") or None  # None = Playwright's own Chromium
VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}


def shot(page: Page, name: str) -> None:
    path = OUT / f"{name}.png"
    # scroll up (a sticky header would otherwise be painted mid-page) and let colour transitions finish
    page.evaluate("window.scrollTo(0, 0)")
    page.mouse.move(0, 0)
    page.wait_for_timeout(400)
    page.screenshot(path=str(path), full_page=True)
    print(f"  screenshot {path}")


def pick(page: Page, name: str) -> None:
    """Click the visible card/chip that wraps the (visually hidden) input, as a user would."""
    page.locator("label").filter(has=page.get_by_label(name, exact=True)).click()


def next_button(page: Page):
    return page.get_by_role("button", name=re.compile(r"^(Next|Review answers|Back to summary)$"))


def run(page: Page, label: str, use_keyboard: bool) -> str:
    print(f"== {label}")
    page.goto(f"{BASE}/planner")
    page.evaluate("sessionStorage.clear()")
    page.reload()

    # Step 1: business type + name
    expect(page.get_by_role("heading", level=1)).to_have_text("What kind of business is it?")
    expect(next_button(page)).to_be_disabled()
    expect(page.get_by_text("Choose a business type to continue.")).to_be_visible()
    pick(page, "Coffee shop")
    page.get_by_label("Business name").fill("Bean There")
    expect(next_button(page)).to_be_enabled()
    shot(page, f"{label}-step1-business")
    next_button(page).click()

    # Step 2: goal (keyboard on one run: focus the first radio, arrow down twice)
    expect(page.get_by_role("heading", level=1)).to_have_text("What should the website do for you first?")
    expect(next_button(page)).to_be_disabled()
    if use_keyboard:
        page.get_by_label("Get bookings").focus()
        page.keyboard.press("Space")
        page.keyboard.press("ArrowDown")
        page.keyboard.press("ArrowUp")
        expect(page.get_by_label("Get bookings")).to_be_checked()
    else:
        pick(page, "Get bookings")
    next_button(page).click()

    # Step 3: audience + languages (limit of 3)
    expect(page.get_by_role("heading", level=1)).to_have_text("Who are your customers?")
    pick(page, "Local")
    pick(page, "German")
    pick(page, "Ukrainian")
    expect(page.get_by_label("French")).to_be_disabled()  # 3 chosen: the rest are locked
    pick(page, "Ukrainian")
    expect(page.get_by_label("French")).to_be_enabled()
    shot(page, f"{label}-step3-audience")
    next_button(page).click()

    # Step 4: features (optional) — reload here to prove progress survives
    expect(page.get_by_role("heading", level=1)).to_have_text("Which features do you want?")
    expect(next_button(page)).to_be_enabled()
    pick(page, "Online booking")
    pick(page, "Map & opening hours")
    page.reload()
    expect(page.get_by_role("heading", level=1)).to_have_text("Which features do you want?")
    expect(page.get_by_label("Online booking")).to_be_checked()
    shot(page, f"{label}-step4-features")
    next_button(page).click()

    # Step 5: budget + timeline
    expect(page.get_by_role("heading", level=1)).to_have_text("What's your budget and timeline?")
    pick(page, "Starter")
    expect(page.get_by_text("Choose a timeline to continue.")).to_be_visible()
    pick(page, "As soon as possible")
    next_button(page).click()

    # Summary, then edit one answer and come back
    expect(page.get_by_role("heading", level=1)).to_have_text("Check your answers")
    expect(page.get_by_text('Coffee shop, "Bean There"')).to_be_visible()
    expect(page.get_by_text("Local, in English, German")).to_be_visible()
    page.get_by_role("button", name="Edit budget and timeline").click()
    pick(page, "Within a month")
    page.get_by_role("button", name="Back to summary").click()
    expect(page.get_by_text("Starter, within a month")).to_be_visible()
    shot(page, f"{label}-summary")

    # Submit
    page.get_by_role("button", name="Generate my plan").click()
    page.wait_for_url(re.compile(r"/plan/[a-z0-9]{10}$"), timeout=15000)
    plan_id = page.url.rsplit("/", 1)[1]
    print(f"  submitted -> {page.url}")
    shot(page, f"{label}-plan-page")

    # After a successful submit the wizard starts fresh
    page.goto(f"{BASE}/planner")
    expect(page.get_by_role("heading", level=1)).to_have_text("What kind of business is it?")
    expect(page.get_by_label("Coffee shop")).not_to_be_checked()
    expect(page.get_by_label("Business name")).to_have_value("")
    print("  /planner after submit: fresh start")
    return plan_id


def check_error_states(page: Page) -> None:
    """Fake API failures in the browser: the wizard must explain them and keep the answers."""
    print("== error states")
    page.goto(f"{BASE}/planner")
    page.evaluate("sessionStorage.clear()")

    # 1) options can't load -> error with retry
    fail = {"on": True}
    page.route("**/api/options", lambda route: route.fulfill(status=503, body="")
               if fail["on"] else route.continue_())
    page.reload()
    expect(page.get_by_role("heading", name="The planner couldn't load")).to_be_visible()
    fail["on"] = False
    page.get_by_role("button", name="Try again").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("What kind of business is it?")
    print("  options 503 -> error + retry works")

    # 2) plan can't be created -> friendly message, answers kept
    page.route("**/api/plans", lambda route: route.fulfill(
        status=500, content_type="application/json", body='{"detail": "Something broke."}'))
    pick(page, "Restaurant")
    next_button(page).click()
    pick(page, "Get leads / calls")
    next_button(page).click()
    pick(page, "National")
    next_button(page).click()
    next_button(page).click()
    pick(page, "Standard")
    pick(page, "Flexible")
    next_button(page).click()
    page.get_by_role("button", name="Generate my plan").click()
    expect(page.get_by_role("alert")).to_contain_text("We couldn't build your plan.")
    expect(page.get_by_role("alert")).to_contain_text("Your answers are saved")
    expect(page.get_by_text("Restaurant")).to_be_visible()
    assert "/planner" in page.url
    print("  plans 500 -> friendly error, still on the summary with answers")
    page.unroute_all()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox", "--disable-dev-shm-usage"])
        ids = []
        for i, (label, (w, h)) in enumerate(VIEWPORTS.items()):
            page = browser.new_page(viewport={"width": w, "height": h})
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            ids.append(run(page, label, use_keyboard=(i == 0)))
            if errors:
                raise SystemExit(f"Console errors on {label}: {errors}")
            no_hscroll = page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            print(f"  console errors: 0, no horizontal scroll: {no_hscroll}")
            page.close()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        check_error_states(page)
        page.close()
        browser.close()
    print("PLAN IDS:", " ".join(ids))


if __name__ == "__main__":
    main()
