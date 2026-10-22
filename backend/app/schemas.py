"""Pydantic models: wizard input, generated plan, API responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BusinessType = Literal[
    "coffee_shop", "restaurant", "beauty_salon", "online_store", "local_services", "freelancer", "consulting"
]
Goal = Literal["bookings", "sell_online", "leads", "brand", "portfolio"]
Audience = Literal["local", "national", "international"]
Language = Literal["en", "de", "fr", "es", "it", "pl", "sk", "cs", "uk"]
Feature = Literal[
    "booking", "payments", "blog", "gallery", "reviews", "map_hours", "contact_form", "multilingual", "newsletter"
]
Budget = Literal["starter", "standard", "advanced"]
Timeline = Literal["asap", "one_month", "flexible"]
SiteTypeId = Literal["landing_page", "business_site", "booking_site", "ecommerce", "portfolio"]
Priority = Literal["must", "nice"]


# ---------- input ----------

class PlanInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business_type: BusinessType
    goal: Goal
    audience: Audience
    languages: list[Language] = Field(default_factory=lambda: ["en"], min_length=1, max_length=3)
    features: list[Feature] = Field(default_factory=list, max_length=9)
    budget: Budget
    timeline: Timeline
    business_name: str | None = Field(default=None, max_length=60)

    @field_validator("languages", "features")
    @classmethod
    def no_duplicates(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("Each option can be chosen only once")
        return value

    @field_validator("business_name", mode="before")
    @classmethod
    def trim_name(cls, value: object) -> object:
        # "  Bean There " -> "Bean There"; blank -> not given
        if isinstance(value, str):
            return value.strip() or None
        return value


# ---------- generated plan ----------

class SiteType(BaseModel):
    id: SiteTypeId
    name: str
    why: str


class Complexity(BaseModel):
    score: int = Field(ge=1, le=10)
    label: Literal["Simple", "Moderate", "Complex"]
    estimated_weeks: str
    why: str


class Page(BaseModel):
    key: str  # stable page id from the engine's PAGE_LIBRARY, e.g. "home", "menu", "booking", "legal"
    name: str
    slug: str
    priority: Literal["launch", "later"]
    required: bool  # always "launch" and never counted in page totals (Privacy & imprint, Shipping & returns)
    sections: list[str]
    why: str

    @model_validator(mode="before")
    @classmethod
    def fill_required_for_old_plans(cls, data: object) -> object:
        # Plans saved before engine 1.3.0 have no flag; Legal and Shipping were the only required pages then.
        if isinstance(data, dict) and "required" not in data:
            return {**data, "required": data.get("key") in ("legal", "shipping")}
        return data


class FeatureItem(BaseModel):
    id: Feature
    name: str
    priority: Priority
    recommended: bool  # True = the user didn't pick it, the engine suggests it
    why: str


class ContentIdeas(BaseModel):
    page: str
    ideas: list[str]


class SeoItem(BaseModel):
    id: str
    title: str
    category: Literal["basics", "local", "content", "technical"]
    why: str


class NextStep(BaseModel):
    title: str
    why: str


class PlanResult(BaseModel):
    summary: str
    site_type: SiteType
    complexity: Complexity
    sitemap: list[Page]
    features: list[FeatureItem]
    content_ideas: list[ContentIdeas]
    seo_checklist: list[SeoItem]
    next_steps: list[NextStep]


# ---------- API responses ----------

class PlanCreated(BaseModel):
    id: str
    plan: PlanResult


class ExampleSite(BaseModel):
    domain: str
    url: str
    title: str
    summary: str
    dr: int | None


class ExamplesResponse(BaseModel):
    items: list[ExampleSite]
    source: Literal["FreeSerp"]
    cached: bool


class SavedPlan(BaseModel):
    id: str
    created_at: datetime
    engine_version: str
    input: PlanInput
    plan: PlanResult
