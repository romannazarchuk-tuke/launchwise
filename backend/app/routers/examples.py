"""GET /api/examples: similar live sites for a business type (via FreeSerp)."""

from fastapi import APIRouter, Query

from app.schemas import BusinessType, ExamplesResponse
from app.services.freeserp import get_examples

router = APIRouter(tags=["examples"])


@router.get("/examples", response_model=ExamplesResponse)
def examples(business_type: BusinessType = Query(...)) -> ExamplesResponse:
    items, cached = get_examples(business_type)
    return ExamplesResponse(items=items, source="FreeSerp", cached=cached)
