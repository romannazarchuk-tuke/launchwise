"""End-to-end checks for the /plan/:id result page (Playwright).

Usage (from the repo root):
    uv run --with playwright python qa/plan_e2e.py [BASE_URL] [OUT_DIR]

Covers: all tabs, tab survives reload, SEO progress survives reload, copy brief, both downloads,
share link, "Start a new plan" opens an empty wizard, not-found, and that page counts are the same
everywhere (summary, At a glance, Sitemap groups, export). Saves the screenshots for the report.
"""

import re
import os
import sys
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("QA_BASE_URL", "http://localhost:5173")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "qa/screenshots")
CHROMIUM = os.environ.get("CHROMIUM_PATH") or None  # None = Playwright's own Chromium
DEMO_PLANS = {"coffee": "l34kndqa5h", "store": "5djzwcux94", "freelancer": "4ljr4niwhx"}
TABS = ["Overview", "Sitemap", "Features", "Content", "SEO checklist", "Examples"]


def join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def expected_counts(sitemap: list[dict]) -> tuple[str, str, str]:
    """Independent re-implementation from the raw API data: (full text, launch group, later group)."""
    launch = [p for p in sitemap if p["priority"] == "launch" and not p["required"]]
    required = [p["name"] for p in sitemap if p["required"]]
    later = [p for p in sitemap if p["priority"] == "later"]
    group = plural(len(launch), "page") + (f" + required {join(required)}" if required else "")
    full = f"{plural(len(launch), 'page')} at launch" + (f" + required {join(required)}" if required else "")
    full += f", {len(later)} later" if later else ""
    return full, group, plural(len(later), "page")


def shot(page: Page, name: str) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    page.mouse.move(0, 0)
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    print(f"  screenshot {OUT / name}.png")


def tab(page: Page, name: str):
    return page.get_by_role("tab", name=name)


def open_tab(page: Page, name: str) -> None:
    tab(page, name).click()
    expect(tab(page, name)).to_have_attribute("aria-selected", "true")


def check_counts(page: Page, plan_id: str) -> None:
    data = page.request.get(f"{BASE}/api/plans/{plan_id}").json()
    full, group, later_group = expected_counts(data["plan"]["sitemap"])
    page.goto(f"{BASE}/plan/{plan_id}")
    expect(page.get_by_test_id("page-counts")).to_have_text(full)                 # At a glance
    expect(page.get_by_text(data["plan"]["summary"])).to_be_visible()
    assert f"The plan: {full}." in data["plan"]["summary"], "summary uses a different count"
    open_tab(page, "Sitemap")
    expect(page.get_by_test_id("sitemap-counts")).to_have_text(full)              # line above the tree
    expect(page.get_by_test_id("launch-heading-count")).to_have_text(group)       # Launch group
    if "later" in full:
        expect(page.get_by_test_id("later-heading-count")).to_have_text(later_group)
    for fmt in ("md", "txt"):
        text = page.request.get(f"{BASE}/api/plans/{plan_id}/export?format={fmt}").text()
        assert f"Pages: {full}." in text and f"Launch now: {group}" in text, f"export .{fmt} disagrees"
    print(f"  counts agree everywhere: {full!r}")


def check_all_tabs(page: Page, plan_id: str) -> None:
    page.goto(f"{BASE}/plan/{plan_id}")
    checks = {
        "Overview": page.get_by_role("heading", name="Next steps"),
        "Sitemap": page.get_by_role("heading", name=re.compile("^Launch now")),
        "Features": page.get_by_role("heading", name="Must-have"),
        "Content": page.get_by_role("heading", name="Home", exact=True),
        "SEO checklist": page.get_by_test_id("seo-progress"),
        "Examples": page.get_by_text(re.compile("Site authority|No example sites right now")).first,
    }
    for name in TABS:
        open_tab(page, name)
        expect(checks[name]).to_be_visible(timeout=15000)
    # keyboard: arrow keys move between tabs
    tab(page, "Examples").focus()
    page.keyboard.press("Home")
    expect(tab(page, "Overview")).to_have_attribute("aria-selected", "true")
    page.keyboard.press("ArrowRight")
    expect(tab(page, "Sitemap")).to_have_attribute("aria-selected", "true")
    print("  all 6 tabs render; arrow keys work")

    # the tab survives a reload (it lives in ?tab=)
    open_tab(page, "Features")
    page.reload()
    expect(tab(page, "Features")).to_have_attribute("aria-selected", "true")
    assert "tab=features" in page.url
    print("  tab survives reload")


def check_seo_progress(page: Page, plan_id: str) -> None:
    page.goto(f"{BASE}/plan/{plan_id}?tab=seo")
    total = len(page.request.get(f"{BASE}/api/plans/{plan_id}").json()["plan"]["seo_checklist"])
    expect(page.get_by_test_id("seo-progress")).to_have_text(f"0 of {total} done")
    boxes = page.get_by_role("tabpanel").get_by_role("checkbox")
    boxes.nth(0).check()
    boxes.nth(2).check()
    expect(page.get_by_test_id("seo-progress")).to_have_text(f"2 of {total} done")
    page.reload()
    expect(page.get_by_test_id("seo-progress")).to_have_text(f"2 of {total} done")
    expect(boxes.nth(2)).to_be_checked()
    page.get_by_role("button", name="Clear checklist").click()
    expect(page.get_by_test_id("seo-progress")).to_have_text(f"0 of {total} done")
    print(f"  SEO progress survives reload (2 of {total}), clear works")


def check_actions(page: Page, plan_id: str) -> None:
    page.goto(f"{BASE}/plan/{plan_id}")
    full, _, _ = expected_counts(page.request.get(f"{BASE}/api/plans/{plan_id}").json()["plan"]["sitemap"])

    page.get_by_role("button", name="Copy brief").click()
    expect(page.get_by_role("status")).to_have_text("Copied!")
    clip = page.evaluate("navigator.clipboard.readText()")
    assert clip.startswith("# Website plan") and f"Pages: {full}." in clip, "clipboard doesn't hold the brief"
    print(f"  copy brief: {len(clip)} characters on the clipboard, toast shown")

    for fmt in ("md", "txt"):
        with page.expect_download() as info:
            page.get_by_role("link", name=f"Download .{fmt}").click()
        download = info.value
        assert download.suggested_filename == f"launchwise-plan-{plan_id}.{fmt}", download.suggested_filename
        content = Path(download.path()).read_text()
        assert f"Pages: {full}." in content
        print(f"  download .{fmt}: {download.suggested_filename} ({len(content)} characters)")

    page.get_by_role("button", name="Copy share link").click()
    expect(page.get_by_role("status")).to_have_text("Link copied")
    assert page.evaluate("navigator.clipboard.readText()") == f"{BASE}/plan/{plan_id}"
    print("  share link copied")


def check_start_new(page: Page, plan_id: str) -> None:
    # leave half-finished answers in the wizard first, so we can see them cleared
    page.goto(f"{BASE}/planner")
    page.locator("label").filter(has=page.get_by_label("Restaurant", exact=True)).click()
    page.get_by_label("Business name").fill("Old answers")
    page.goto(f"{BASE}/plan/{plan_id}")
    page.get_by_role("button", name="Start a new plan").click()
    page.wait_for_url(f"{BASE}/planner")
    expect(page.get_by_role("heading", level=1)).to_have_text("What kind of business is it?")
    expect(page.get_by_label("Restaurant", exact=True)).not_to_be_checked()
    expect(page.get_by_label("Business name")).to_have_value("")
    print("  Start a new plan -> empty wizard")


def check_not_found(page: Page) -> None:
    for bad in ("zzzzzzzzzz", "BAD-ID"):
        page.goto(f"{BASE}/plan/{bad}")
        expect(page.get_by_role("heading", name="Plan not found")).to_be_visible()
        expect(page.get_by_role("link", name="Start a new plan")).to_be_visible()
    print("  unknown and malformed ids -> Plan not found")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox", "--disable-dev-shm-usage"])
        errors: list[str] = []

        def new_page(width: int, height: int) -> Page:
            context = browser.new_context(viewport={"width": width, "height": height}, accept_downloads=True)
            context.grant_permissions(["clipboard-read", "clipboard-write"], origin=BASE)
            page = context.new_page()
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            return page

        print("== desktop 1440")
        page = new_page(1440, 900)
        for name, plan_id in DEMO_PLANS.items():
            print(f"-- {name} ({plan_id})")
            check_counts(page, plan_id)
            shot(page, f"sitemap-{name}-1440")  # check_counts leaves the Sitemap tab open
        coffee = DEMO_PLANS["coffee"]
        check_all_tabs(page, coffee)
        check_seo_progress(page, coffee)
        check_actions(page, coffee)
        check_start_new(page, coffee)
        before = len(errors)
        check_not_found(page)
        # the browser logs the deliberate 404/422 API responses; anything else still fails the run
        expected = re.compile(r"Failed to load resource: .*status of (404|422)")
        errors[before:] = [e for e in errors[before:] if not expected.search(e)]

        print("== mobile 390")
        page = new_page(390, 844)
        page.goto(f"{BASE}/plan/{coffee}")
        expect(page.get_by_role("heading", name="Next steps")).to_be_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "horizontal scroll"
        shot(page, "overview-coffee-390")
        open_tab(page, "Examples")  # last tab: the strip must scroll it into view
        box = tab(page, "Examples").bounding_box()
        assert box and box["x"] + box["width"] <= 390, "active tab not scrolled into view"
        open_tab(page, "Sitemap")
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "horizontal scroll"
        shot(page, "sitemap-coffee-390")
        print("  no horizontal scroll; tab strip scrolls to the active tab")

        if errors:
            raise SystemExit(f"Console errors: {errors}")
        print("console errors: 0")
        browser.close()
    print("ALL PLAN CHECKS PASSED")


if __name__ == "__main__":
    main()
