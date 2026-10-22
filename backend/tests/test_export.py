"""The export uses the same page-count text as the summary."""

from app.export import render
from app.rules import ENGINE_VERSION, generate_plan, page_counts_text
from app.schemas import PlanInput


def test_export_uses_the_same_page_counts():
    inp = PlanInput(business_type="coffee_shop", goal="bookings", audience="local",
                    features=["booking", "map_hours"], budget="starter", timeline="asap")
    plan = generate_plan(inp)
    text = page_counts_text(plan.sitemap)
    for markdown in (True, False):
        out = render("abcdefghij", inp, plan, ENGINE_VERSION, markdown=markdown)
        assert f"Pages: {text}." in out
        assert "Launch now: 4 pages + required Privacy & imprint" in out
        assert "Later: 4 pages" in out
        assert out.count(text) == 2  # the Sitemap line and the summary
