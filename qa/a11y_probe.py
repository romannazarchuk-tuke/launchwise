"""Accessibility probe (WCAG 2.1 AA helpers): contrast of the design tokens, small touch targets,
visible focus on every Tab stop, and 200 % zoom (720 px wide) without horizontal scrolling.

Usage: uv run --with playwright python qa/a11y_probe.py [BASE_URL]
"""

import os
import sys

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("QA_BASE_URL", "http://localhost:5173")
PAGES = {"home": "/", "planner": "/planner", "result": "/plan/l34kndqa5h", "about": "/about"}


def luminance(hex_color: str) -> float:
    rgb = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(fg: str, bg: str) -> float:
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


PAIRS = [  # (element, fg, bg, required)
    ("Body text (ink on paper)", "#1E1B2E", "#FAFAFC", 4.5),
    ("Secondary text (muted on paper)", "#615C75", "#FAFAFC", 4.5),
    ("Secondary text (muted on white)", "#615C75", "#FFFFFF", 4.5),
    ("Primary button (white on violet)", "#FFFFFF", "#6D4AFF", 4.5),
    ("Links / badges (violet-deep on violet-50)", "#4B2FD1", "#F1EDFF", 4.5),
    ("Links (violet-deep on white)", "#4B2FD1", "#FFFFFF", 4.5),
    ("Page card: lilac", "#5B3CC4", "#EEE8FF", 4.5),
    ("Page card: sky", "#1E5FAD", "#E2F0FF", 4.5),
    ("Page card: mint", "#127A55", "#DFF6EC", 4.5),
    ("Page card: peach", "#B4532A", "#FFE9DC", 4.5),
    ("Page card: butter", "#7A5D00", "#FFF4CC", 4.5),
    ("Page card: stone", "#615C75", "#F0EFF4", 4.5),
    ("Focus ring / selected border (violet on white)", "#6D4AFF", "#FFFFFF", 3.0),
    ("Card border (line on white) - decorative", "#E6E3F0", "#FFFFFF", 0),
]


def main() -> None:
    print("== contrast")
    for name, fg, bg, need in PAIRS:
        r = ratio(fg, bg)
        verdict = "n/a" if need == 0 else ("PASS" if r >= need else "FAIL")
        print(f"  {name:48} {fg} on {bg}: {r:5.2f}:1 (need {need}) {verdict}")

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        for name, path in PAGES.items():
            page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
            page.goto(f"{BASE}{path}")
            page.wait_for_load_state("networkidle")

            small = page.evaluate("""() => [...document.querySelectorAll('a, button, input, [role=tab], label:has(input)')]
              .filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'
                              && !el.classList.contains('sr-only') && (r.height < 44 || r.width < 44); })
              .filter(el => !(el.tagName === 'INPUT' && el.closest('label')))   // the label is the target
              .map(el => `${el.tagName.toLowerCase()} "${(el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 28)}" ${Math.round(el.getBoundingClientRect().width)}x${Math.round(el.getBoundingClientRect().height)}`)""")
            print(f"== {name}: targets under 44 px ({len(small)})")
            for s in sorted(set(small))[:14]:
                print("   ", s)

            # Tab through the page: every stop must show an outline or a ring/border change
            missing, stops = [], 0
            page.keyboard.press("Tab")
            for _ in range(60):
                info = page.evaluate("""() => { const el = document.activeElement; if (!el || el === document.body) return null;
                    const target = (el.matches('input.sr-only') && el.closest('label')) || el;  // hidden inputs show focus on their card
                    const s = getComputedStyle(target);
                    const outline = s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0;
                    return {name: `${el.tagName.toLowerCase()} "${(el.innerText || el.getAttribute('aria-label') || el.value || '').trim().slice(0, 30)}"`,
                            visible: outline || s.boxShadow !== 'none'}; }""")
                if info is None:
                    break
                stops += 1
                if not info["visible"]:
                    missing.append(info["name"])
                page.keyboard.press("Tab")
            print(f"   tab stops checked: {stops}; without a visible focus indicator: {missing or 'none'}")

            zoom = browser.new_context(viewport={"width": 720, "height": 450}).new_page()
            zoom.goto(f"{BASE}{path}")
            zoom.wait_for_load_state("networkidle")
            overflow = zoom.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            print(f"   200% zoom (720 px): horizontal overflow {overflow}px")
            zoom.context.close()
            page.context.close()
        browser.close()


if __name__ == "__main__":
    main()
