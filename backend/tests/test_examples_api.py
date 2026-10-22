"""GET /api/examples contract. FreeSerp is faked; no network and no database needed."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import freeserp

client = TestClient(app)


@pytest.fixture(autouse=True)
def empty_cache():
    freeserp._cache.clear()
    yield
    freeserp._cache.clear()


def test_freeserp_down_gives_empty_list_not_error(monkeypatch):
    def down(*a, **k):
        raise httpx.ConnectError("Name or service not known")

    monkeypatch.setattr(freeserp.httpx, "get", down)
    r = client.get("/api/examples", params={"business_type": "coffee_shop"})
    assert r.status_code == 200
    assert r.json() == {"items": [], "source": "FreeSerp", "cached": False}


@pytest.mark.parametrize("params", [{"business_type": "bakery"}, {}])
def test_bad_business_type_is_422(params):
    r = client.get("/api/examples", params=params)
    assert r.status_code == 422
    assert r.json()["errors"][0]["field"] == "business_type"


def test_unexpected_error_is_json_without_details(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr("app.routers.examples.get_examples", boom)
    r = TestClient(app, raise_server_exceptions=False).get("/api/examples", params={"business_type": "coffee_shop"})
    assert r.status_code == 500
    assert r.json() == {"detail": "Something went wrong on our side. Please try again."}
    assert "secret" not in r.text and "Traceback" not in r.text
