"""FreeSerp client tests. No real network: httpx.get is replaced with fakes."""

import httpx
import pytest

from app.services import freeserp


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status_code = payload, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=httpx.Request("GET", "https://x"), response=None)

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


@pytest.fixture(autouse=True)
def empty_cache():
    freeserp._cache.clear()
    yield
    freeserp._cache.clear()


def payload(*results):
    return {"ok": True, "results": list(results)}


GOOD = {"domain": "miamcafe.com", "url": "https://miamcafe.com", "title": "MIAM Cafe | Miami",
        "ai_summary": "A cosy coffee shop. " * 20, "dr": 24, "http_status": 200}


def test_maps_fields_and_shortens_summary(monkeypatch):
    monkeypatch.setattr(freeserp.httpx, "get", lambda *a, **k: FakeResponse(payload(GOOD)))
    items, cached = freeserp.get_examples("coffee_shop")
    assert cached is False
    assert items == [{
        "domain": "miamcafe.com", "url": "https://miamcafe.com", "title": "MIAM Cafe | Miami",
        "summary": items[0]["summary"], "dr": 24,
    }]
    assert len(items[0]["summary"]) <= freeserp.SUMMARY_MAX + 1 and items[0]["summary"].endswith("…")


def test_drops_results_without_title_or_non_200(monkeypatch):
    results = [
        GOOD,
        {**GOOD, "domain": "a.com", "title": ""},
        {**GOOD, "domain": "b.com", "title": None},
        {**GOOD, "domain": "c.com", "http_status": 404},
        {**GOOD, "domain": "d.com", "http_status": "200"},           # string status is fine
        {k: v for k, v in GOOD.items() if k != "http_status"} | {"domain": "e.com"},  # no field: keep
        {**GOOD, "domain": "f.com", "dr": None, "ai_summary": None},  # missing optional data: keep
    ]
    monkeypatch.setattr(freeserp.httpx, "get", lambda *a, **k: FakeResponse(payload(*results)))
    items, _ = freeserp.get_examples("coffee_shop")
    assert [i["domain"] for i in items] == ["miamcafe.com", "d.com", "e.com", "f.com"]
    assert items[-1]["dr"] is None and items[-1]["summary"] == ""


def test_sends_query_and_identification(monkeypatch):
    seen = {}

    def fake_get(url, params, timeout):
        seen.update(url=url, params=params, timeout=timeout)
        return FakeResponse(payload(GOOD))

    monkeypatch.setattr(freeserp.httpx, "get", fake_get)
    freeserp.get_examples("beauty_salon")
    assert seen["params"]["q"] == "beauty salon hair nails"
    assert seen["params"]["size"] == freeserp.CANDIDATES and seen["params"]["sort"] == "relevance"
    assert seen["params"]["agent"] == "LaunchWise/1.0" and seen["params"]["project"] == "LaunchWise"
    assert seen["timeout"] == 5.0


@pytest.mark.parametrize("bad", [
    {"domain": "cbd.co", "title": "Shop CBD products"},
    {"title": "Adult Store | Sex Shop Online"},
    {"ai_summary": "A recreational cannabis dispensary."},
    {"category": "betting/casino"},
    {"ai_summary": "The page displays a verification message."},
    {"ai_summary": "The page displays a basic HTML structure with an Open Graph tag."},
    {"ai_summary": "The site is a directory that helps users find pros."},
    {"title": "こだわりの果物屋 紅光（べにこう）"},
])
def test_filters_unsuitable_sites(monkeypatch, bad):
    monkeypatch.setattr(freeserp.httpx, "get", lambda *a, **k: FakeResponse(payload({**GOOD, **bad})))
    assert freeserp.get_examples("coffee_shop") == ([], False)


@pytest.mark.parametrize("ok", [
    {"title": "Café Crème – Kaffeehaus in Zürich"},        # accented Latin is fine
    {"ai_summary": "A tea room in Sussex and Essex."},      # "sex" only as a whole word
])
def test_keeps_normal_sites(monkeypatch, ok):
    monkeypatch.setattr(freeserp.httpx, "get", lambda *a, **k: FakeResponse(payload({**GOOD, **ok})))
    items, _ = freeserp.get_examples("coffee_shop")
    assert len(items) == 1


def test_returns_at_most_six(monkeypatch):
    many = [{**GOOD, "domain": f"site{i}.com"} for i in range(15)]
    monkeypatch.setattr(freeserp.httpx, "get", lambda *a, **k: FakeResponse(payload(*many)))
    items, _ = freeserp.get_examples("coffee_shop")
    assert [i["domain"] for i in items] == [f"site{i}.com" for i in range(freeserp.RESULT_SIZE)]


def test_second_call_is_cached(monkeypatch):
    calls = []
    monkeypatch.setattr(freeserp.httpx, "get", lambda *a, **k: calls.append(1) or FakeResponse(payload(GOOD)))
    first, cached1 = freeserp.get_examples("coffee_shop")
    second, cached2 = freeserp.get_examples("coffee_shop")
    assert (cached1, cached2) == (False, True) and first == second and len(calls) == 1


def test_cache_expires(monkeypatch):
    calls = []
    monkeypatch.setattr(freeserp.httpx, "get", lambda *a, **k: calls.append(1) or FakeResponse(payload(GOOD)))
    freeserp.get_examples("coffee_shop")
    now = freeserp.time.monotonic()
    monkeypatch.setattr(freeserp.time, "monotonic", lambda: now + freeserp.CACHE_TTL_S + 1)
    _, cached = freeserp.get_examples("coffee_shop")
    assert cached is False and len(calls) == 2


@pytest.mark.parametrize("failure", [
    httpx.ConnectError("no route to host"),
    httpx.ReadTimeout("timed out"),
    FakeResponse({"ok": False, "error": "upstream"}, status=502),
    FakeResponse({"ok": False, "error": "upstream"}),
    FakeResponse(ValueError("not json")),
])
def test_any_failure_gives_empty_list(monkeypatch, failure):
    def fake_get(*a, **k):
        if isinstance(failure, Exception):
            raise failure
        return failure

    monkeypatch.setattr(freeserp.httpx, "get", fake_get)
    assert freeserp.get_examples("restaurant") == ([], False)


def test_failure_is_cached_only_briefly(monkeypatch):
    calls = []

    def failing(*a, **k):
        calls.append(1)
        raise httpx.ConnectError("down")

    monkeypatch.setattr(freeserp.httpx, "get", failing)
    freeserp.get_examples("restaurant")
    freeserp.get_examples("restaurant")
    assert len(calls) == 1  # second call served from the short failure cache
    now = freeserp.time.monotonic()
    monkeypatch.setattr(freeserp.time, "monotonic", lambda: now + freeserp.FAILURE_TTL_S + 1)
    freeserp.get_examples("restaurant")
    assert len(calls) == 2


def test_every_business_type_has_a_query():
    from app import catalog
    assert set(freeserp.QUERY_BY_BUSINESS) == set(catalog.BUSINESS_TYPES)
