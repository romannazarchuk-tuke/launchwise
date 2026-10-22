"""GET /api/options: every wizard choice with label, description and icon."""

from fastapi import APIRouter

from app import catalog

router = APIRouter(tags=["options"])


def _as_list(choices: dict) -> list[dict]:
    return [{"id": key, **value} for key, value in choices.items()]


@router.get("/options")
def get_options() -> dict:
    return {
        "business_types": _as_list(catalog.BUSINESS_TYPES),
        "goals": _as_list(catalog.GOALS),
        "audiences": _as_list(catalog.AUDIENCES),
        "languages": _as_list(catalog.LANGUAGES),
        "features": _as_list(catalog.FEATURES),
        "budgets": _as_list(catalog.BUDGETS),
        "timelines": _as_list(catalog.TIMELINES),
        "limits": {"languages_min": 1, "languages_max": 3, "business_name_max": 60},
    }
