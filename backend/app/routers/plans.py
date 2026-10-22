"""Plans API: create, load and export website plans."""

import secrets
import string
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.export import render
from app.models import Plan
from app.rules import ENGINE_VERSION, generate_plan
from app.schemas import PlanCreated, PlanInput, PlanResult, SavedPlan

router = APIRouter(prefix="/plans", tags=["plans"])

ID_ALPHABET = string.ascii_lowercase + string.digits
ID_LENGTH = 10
PlanId = Annotated[str, Path(pattern=rf"^[a-z0-9]{{{ID_LENGTH}}}$")]


def new_plan_id(db: Session) -> str:
    # 36^10 possible ids, so a collision is practically impossible; we still check.
    while True:
        plan_id = "".join(secrets.choice(ID_ALPHABET) for _ in range(ID_LENGTH))
        if db.get(Plan, plan_id) is None:
            return plan_id


def load_plan(db: Session, plan_id: str) -> Plan:
    plan = db.get(Plan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.post("", status_code=201, response_model=PlanCreated)
def create_plan(answers: PlanInput, db: Session = Depends(get_db)) -> PlanCreated:
    result = generate_plan(answers)
    row = Plan(
        id=new_plan_id(db),
        input_json=answers.model_dump(mode="json"),
        result_json=result.model_dump(mode="json"),
        engine_version=ENGINE_VERSION,
    )
    db.add(row)
    db.commit()
    return PlanCreated(id=row.id, plan=result)


@router.get("/{plan_id}", response_model=SavedPlan)
def get_plan(plan_id: PlanId, db: Session = Depends(get_db)) -> SavedPlan:
    row = load_plan(db, plan_id)
    return SavedPlan(id=row.id, created_at=row.created_at, engine_version=row.engine_version,
                     input=row.input_json, plan=row.result_json)


@router.get("/{plan_id}/export")
def export_plan(
    plan_id: PlanId,
    format: Literal["md", "txt"] = Query("md"),
    db: Session = Depends(get_db),
) -> Response:
    row = load_plan(db, plan_id)
    text = render(row.id, PlanInput(**row.input_json), PlanResult(**row.result_json),
                  row.engine_version, markdown=format == "md")
    media_type = "text/markdown" if format == "md" else "text/plain"
    return Response(
        content=text,
        media_type=f"{media_type}; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="launchwise-plan-{row.id}.{format}"'},
    )
