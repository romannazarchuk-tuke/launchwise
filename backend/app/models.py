"""SQLAlchemy models. The schema itself is created by backend/sql/*.sql (no auto create_all)."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CHAR, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Plan(Base):
    """One generated website plan (see sql/001_create_plans.sql)."""

    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(CHAR(10), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp(), index=True
    )
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    engine_version: Mapped[str] = mapped_column(String(16), nullable=False)
