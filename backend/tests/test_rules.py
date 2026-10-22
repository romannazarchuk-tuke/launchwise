"""Rule engine tests: three reference scenarios, the core sitemap/feature rules and edge cases."""

import itertools

import pytest

from app import catalog
from app.rules import LANDING_HOME_SECTIONS, LAUNCH_PAGE_LIMIT, PAGE_LIBRARY, generate_plan, page_counts_text
from app.schemas import PlanInput


def make(**overrides) -> PlanInput:
    answers = dict(business_type="coffee_shop", goal="bookings", audience="local", languages=["en"],
                   features=[], budget="starter", timeline="asap")
    answers.update(overrides)
    return PlanInput(**answers)


def launch_names(plan) -> list[str]:
    return [p.name for p in plan.sitemap if p.priority == "launch"]


def feature(plan, feature_id):
    return next(f for f in plan.features if f.id == feature_id)


# ---------- the three scenarios ----------

def test_scenario_a_coffee_shop():
    plan = generate_plan(make(features=["booking", "map_hours"], business_name="Bean There"))
    assert plan.site_type.id == "booking_site"
    assert [p.key for p in plan.sitemap if p.priority == "launch"] == ["home", "menu", "booking", "visit", "legal"]
    assert launch_names(plan) == ["Home", "Menu", "Reserve a table", "Visit us", "Privacy & imprint"]
    assert plan.complexity.score == 4 and plan.complexity.label == "Moderate"
    assert plan.summary.startswith("Bean There needs")
    assert feature(plan, "reviews").recommended and feature(plan, "gallery").recommended
    seo_ids = {s.id for s in plan.seo_checklist}
    assert {"google_business_profile", "nap", "local_keywords", "menu_text"} <= seo_ids
    assert any("coffee shop in <your city>" in s.title for s in plan.seo_checklist)


def test_scenario_b_online_store():
    plan = generate_plan(make(business_type="online_store", goal="sell_online", audience="international",
                              languages=["en", "de", "fr"], features=["payments", "blog", "multilingual"],
                              budget="advanced"))
    assert plan.site_type.id == "ecommerce"
    names = launch_names(plan)
    assert {"Shop", "Product page", "Cart & checkout", "Shipping & returns", "Blog"} <= set(names)
    assert plan.complexity.label == "Complex"
    seo_ids = {s.id for s in plan.seo_checklist}
    assert {"product_schema", "hreflang"} <= seo_ids
    assert "google_business_profile" not in seo_ids


def test_scenario_c_freelancer():
    plan = generate_plan(make(business_type="freelancer", goal="portfolio", audience="national", features=[]))
    assert plan.site_type.id == "portfolio"
    assert launch_names(plan) == ["Home", "Work", "About", "Contact", "Privacy & imprint"]
    # services-rates shares the /services URL with other pages; its key keeps it distinct
    assert [p.key for p in plan.sitemap if p.priority == "later"] == ["services-rates"]
    assert plan.complexity.label == "Simple"
    assert feature(plan, "gallery").priority == "must" and feature(plan, "gallery").recommended
    # the Work page is the gallery: no separate Gallery page
    assert "Gallery" not in [p.name for p in plan.sitemap]


def test_scenarios_are_clearly_different():
    a = generate_plan(make(features=["booking", "map_hours"]))
    b = generate_plan(make(business_type="online_store", goal="sell_online", audience="international",
                           features=["payments", "blog", "multilingual"], budget="advanced"))
    c = generate_plan(make(business_type="freelancer", goal="portfolio", audience="national"))
    assert len({a.site_type.id, b.site_type.id, c.site_type.id}) == 3
    assert len({tuple(launch_names(p)) for p in (a, b, c)}) == 3


# ---------- landing page = Home + Legal ----------

def test_landing_page_is_one_page_plus_legal():
    plan = generate_plan(make(business_type="consulting", goal="leads", audience="national"))
    assert plan.site_type.id == "landing_page"
    assert launch_names(plan) == ["Home", "Privacy & imprint"]
    assert plan.sitemap[0].sections == LANDING_HOME_SECTIONS
    # consulting recommends blog (nice) -> it may only appear as a "later" page
    assert all(p.priority == "later" for p in plan.sitemap if p.name not in ("Home", "Privacy & imprint"))
    assert {p.name for p in plan.sitemap if p.priority == "later"} == {"Blog"}


def test_landing_page_without_feature_pages_has_nothing_later():
    plan = generate_plan(make(business_type="local_services", goal="leads", audience="national"))
    assert plan.site_type.id == "landing_page"
    assert [p.name for p in plan.sitemap] == ["Home", "Privacy & imprint"]


# ---------- Legal is always launched and never counted ----------

@pytest.mark.parametrize("business", list(catalog.BUSINESS_TYPES))
@pytest.mark.parametrize("budget", list(catalog.BUDGETS))
def test_legal_always_launch_and_not_counted(business, budget):
    plan = generate_plan(make(business_type=business, goal="brand", audience="national", budget=budget))
    legal = [p for p in plan.sitemap if p.slug == "/privacy"]
    assert len(legal) == 1 and legal[0].priority == "launch"
    assert "GDPR" in legal[0].why
    required = {"/privacy", "/shipping-returns"} if plan.site_type.id == "ecommerce" else {"/privacy"}
    counted = [p for p in plan.sitemap if p.priority == "launch" and p.slug not in required]
    limit = LAUNCH_PAGE_LIMIT[budget]
    if limit is not None:
        assert len(counted) <= limit


def test_starter_coffee_shop_has_four_pages_plus_legal():
    plan = generate_plan(make(goal="brand"))
    assert len(launch_names(plan)) == LAUNCH_PAGE_LIMIT["starter"] + 1
    assert launch_names(plan)[-1] == "Privacy & imprint"


# ---------- highest priority wins, strongest trigger's why ----------

def test_must_beats_nice_and_uses_strongest_why():
    # restaurant recommends booking as "nice"; goal bookings recommends it as "must"
    plan = generate_plan(make(business_type="restaurant", goal="bookings"))
    booking = feature(plan, "booking")
    assert booking.priority == "must"
    assert booking.why.startswith("Your main goal is bookings")


def test_tie_uses_strongest_trigger():
    # local audience and coffee_shop both recommend map_hours as "must"; audience is the stronger trigger
    plan = generate_plan(make())
    assert feature(plan, "map_hours").why.startswith("Local customers")


def test_each_feature_appears_once():
    plan = generate_plan(make(business_type="beauty_salon", goal="bookings", features=["booking", "gallery"]))
    ids = [f.id for f in plan.features]
    assert len(ids) == len(set(ids))


# ---------- numbers in texts come from the data ----------

@pytest.mark.parametrize("budget", list(catalog.BUDGETS))
@pytest.mark.parametrize("timeline", list(catalog.TIMELINES))
def test_numbers_in_summary_and_steps_match_sitemap(budget, timeline):
    plan = generate_plan(make(business_type="online_store", goal="sell_online", budget=budget, timeline=timeline,
                              features=["blog", "gallery"]))
    n_launch = sum(p.priority == "launch" and not p.required for p in plan.sitemap)
    n_later = sum(p.priority == "later" for p in plan.sitemap)
    text = page_counts_text(plan.sitemap)
    assert text.startswith(f"{n_launch} page")
    assert text.endswith(f", {n_later} later") if n_later else "later" not in text
    assert f"The plan: {text}." in plan.summary
    assert f"the {n_launch} launch pages" in plan.next_steps[1].title


def test_page_counts_change_with_budget():
    counts = [len(launch_names(generate_plan(make(business_type="online_store", goal="sell_online", budget=b,
                                                  features=["blog", "gallery", "newsletter"]))))
              for b in ("starter", "standard", "advanced")]
    assert counts[0] < counts[1] < counts[2]


# ---------- invariants over all combinations ----------

ALL_COMBOS = list(itertools.product(catalog.BUSINESS_TYPES, catalog.GOALS, catalog.AUDIENCES, catalog.BUDGETS))


@pytest.mark.parametrize("business,goal,audience,budget", ALL_COMBOS)
@pytest.mark.parametrize("rich", [False, True])
def test_invariants(business, goal, audience, budget, rich):
    inp = make(business_type=business, goal=goal, audience=audience, budget=budget,
               languages=["en", "de", "fr"] if rich else ["en"],
               features=list(catalog.FEATURES) if rich else [])
    plan = generate_plan(inp)
    assert 1 <= plan.complexity.score <= 10
    assert 10 <= len(plan.seo_checklist) <= 14
    assert 3 <= len(plan.next_steps) <= 5
    assert all(3 <= len(c.ideas) <= 5 for c in plan.content_ideas)
    slugs = [p.slug for p in plan.sitemap]
    assert len(slugs) == len(set(slugs))
    keys = [p.key for p in plan.sitemap]
    assert len(keys) == len(set(keys)) and set(keys) <= set(PAGE_LIBRARY)
    # content ideas exist for exactly the launch pages except Legal, looked up by key
    assert [c.page for c in plan.content_ideas] == [
        p.name for p in plan.sitemap if p.priority == "launch" and p.key != "legal"]
    assert plan.sitemap[0].name == "Home" and plan.sitemap[0].priority == "launch"
    whys = ([plan.site_type.why, plan.complexity.why] + [p.why for p in plan.sitemap]
            + [f.why for f in plan.features] + [s.why for s in plan.seo_checklist] + [s.why for s in plan.next_steps])
    assert all(w.strip() for w in whys)
    # every feature the user picked is in the plan and not marked as "recommended"
    for f in inp.features:
        assert not feature(plan, f).recommended


# ---------- edge cases ----------

def test_no_business_name_uses_generic_subject():
    plan = generate_plan(make())
    assert plan.summary.startswith("Your coffee shop needs")


def test_generic_subject_does_not_repeat_site_type():
    plan = generate_plan(make(business_type="online_store", goal="sell_online"))
    assert plan.summary.startswith("Your shop needs an online store")


def test_multilingual_with_one_language_is_nice_with_hint():
    plan = generate_plan(make(features=["multilingual"]))
    item = feature(plan, "multilingual")
    assert item.priority == "nice" and "only one" in item.why


def test_three_languages_recommend_multilingual_and_hreflang():
    plan = generate_plan(make(languages=["en", "de", "uk"]))
    assert feature(plan, "multilingual").priority == "must"
    assert "hreflang" in {s.id for s in plan.seo_checklist}
    assert plan.sitemap[0].sections[0] == "Header with language switcher"


def test_online_store_stays_ecommerce_for_any_goal():
    for goal in catalog.GOALS:
        assert generate_plan(make(business_type="online_store", goal=goal)).site_type.id == "ecommerce"


def test_plan_is_deterministic():
    assert generate_plan(make(features=["blog"])) == generate_plan(make(features=["blog"]))


# ---------- regressions: page ranking and complexity scoring ----------

GLOW_STUDIO = dict(business_type="beauty_salon", goal="brand", audience="local", languages=["en", "de", "sk"],
                   features=["gallery", "reviews"], budget="standard", timeline="flexible", business_name="Glow Studio")


def test_picked_feature_page_outranks_engine_extras():
    plan = generate_plan(make(**GLOW_STUDIO))
    pages = {p.key: p.priority for p in plan.sitemap}
    assert pages["gallery"] == "launch"  # picked + must
    assert pages["faq"] == "later"       # added by the engine on its own


@pytest.mark.parametrize("business,goal,audience,budget", ALL_COMBOS)
def test_feature_pages_never_lose_to_faq(business, goal, audience, budget):
    plan = generate_plan(make(business_type=business, goal=goal, audience=audience, budget=budget,
                              features=["gallery", "blog", "booking"]))
    pages = {p.key: p.priority for p in plan.sitemap}
    if pages.get("faq") == "launch":
        assert all(pages[k] == "launch" for k in ("gallery", "blog", "booking") if k in pages)


def test_many_pages_bonus_ignores_legal():
    # 6 counted launch pages + Legal = 7 launch pages in total -> no bonus
    plan = generate_plan(make(**GLOW_STUDIO))
    launch = [p for p in plan.sitemap if p.priority == "launch"]
    assert len(launch) == 7 and "launch pages" not in plan.complexity.why


def test_many_pages_bonus_ignores_required_shipping_too():
    plan = generate_plan(make(business_type="online_store", goal="sell_online", budget="advanced",
                              audience="national", features=["blog"]))
    counted = [p for p in plan.sitemap if p.priority == "launch" and p.key not in ("legal", "shipping")]
    assert f"{len(counted)} pages at launch (+1)" in plan.complexity.why


def test_languages_are_counted_once():
    plan = generate_plan(make(**GLOW_STUDIO))
    assert "multiple languages (+2)" in plan.complexity.why
    assert "3 languages" not in plan.complexity.why
    # 2 and 3 languages cost the same
    two = generate_plan(make(**{**GLOW_STUDIO, "languages": ["en", "de"]}))
    assert two.complexity.score == plan.complexity.score


def test_glow_studio_score():
    # booking website 3 + multiple languages 2 + online booking 1 = 6 (was 8 with the double counting)
    plan = generate_plan(make(**GLOW_STUDIO))
    assert plan.complexity.score == 6 and plan.complexity.label == "Moderate"


# ---------- 1.3.0: one definition of page counts ----------

def test_required_flag_marks_only_legal_and_store_shipping():
    for business in catalog.BUSINESS_TYPES:
        plan = generate_plan(make(business_type=business, goal="brand", audience="national"))
        expected = {"legal", "shipping"} if plan.site_type.id == "ecommerce" else {"legal"}
        assert {p.key for p in plan.sitemap if p.required} == expected
        assert all(p.priority == "launch" for p in plan.sitemap if p.required)


def test_page_counts_text_examples():
    a = generate_plan(make(features=["booking", "map_hours"]))
    assert page_counts_text(a.sitemap) == "4 pages at launch + required Privacy & imprint, 4 later"
    b = generate_plan(make(business_type="online_store", goal="sell_online", audience="international",
                           languages=["en", "de", "fr"], features=["payments", "blog", "multilingual"],
                           budget="advanced"))
    assert page_counts_text(b.sitemap) == "8 pages at launch + required Shipping & returns and Privacy & imprint"
    landing = generate_plan(make(business_type="local_services", goal="leads", audience="national"))
    assert page_counts_text(landing.sitemap) == "1 page at launch + required Privacy & imprint"


def test_old_snapshots_get_required_flag():
    from app.schemas import Page
    old = {"key": "legal", "name": "Privacy & imprint", "slug": "/privacy", "priority": "launch",
           "sections": [], "why": "x"}
    assert Page(**old).required is True
    assert Page(**{**old, "key": "menu"}).required is False
