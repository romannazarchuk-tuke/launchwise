"""Input validation tests (PlanInput) and catalog/schema consistency."""

from typing import get_args

import pytest
from pydantic import ValidationError

from app import catalog
from app.schemas import Audience, Budget, BusinessType, Feature, Goal, Language, PlanInput, Timeline

VALID = dict(business_type="coffee_shop", goal="bookings", audience="local",
             features=["booking"], budget="starter", timeline="asap")


def test_valid_input_and_defaults():
    inp = PlanInput(**VALID)
    assert inp.languages == ["en"] and inp.business_name is None


@pytest.mark.parametrize("change", [
    {"business_type": "bakery"},
    {"languages": ["en", "de", "fr", "es"]},
    {"languages": []},
    {"languages": ["en", "en"]},
    {"features": ["booking", "booking"]},
    {"features": ["teleport"]},
    {"business_name": "x" * 200},
    {"business_name": 123},
    {"budget": "huge"},
    {"unexpected": "field"},
])
def test_invalid_input_is_rejected(change):
    with pytest.raises(ValidationError):
        PlanInput(**{**VALID, **change})


def test_business_name_is_trimmed_and_blank_means_none():
    assert PlanInput(**VALID, business_name="  Bean There  ").business_name == "Bean There"
    assert PlanInput(**VALID, business_name="   ").business_name is None
    assert PlanInput(**VALID, business_name=" " + "x" * 60 + " ").business_name == "x" * 60


@pytest.mark.parametrize("literal,choices", [
    (BusinessType, catalog.BUSINESS_TYPES), (Goal, catalog.GOALS), (Audience, catalog.AUDIENCES),
    (Language, catalog.LANGUAGES), (Feature, catalog.FEATURES), (Budget, catalog.BUDGETS),
    (Timeline, catalog.TIMELINES),
])
def test_catalog_matches_schema(literal, choices):
    assert list(get_args(literal)) == list(choices)
