"""Create the three demo plans (same ids and answers as on the live site). Safe to run again.

Usage (from backend/): .venv/bin/python -m scripts.seed_demo
"""

from app.db import SessionLocal
from app.models import Plan
from app.rules import ENGINE_VERSION, generate_plan
from app.schemas import PlanInput

DEMO_PLANS = {
    "l34kndqa5h": dict(business_type="coffee_shop", goal="bookings", audience="local", languages=["en"],
                       features=["booking", "map_hours"], budget="starter", timeline="asap", business_name="Bean There"),
    "5djzwcux94": dict(business_type="online_store", goal="sell_online", audience="international",
                       languages=["en", "de", "fr"], features=["payments", "blog", "multilingual"],
                       budget="advanced", timeline="one_month"),
    "4ljr4niwhx": dict(business_type="freelancer", goal="portfolio", audience="national", languages=["en"],
                       features=[], budget="starter", timeline="flexible"),
}


def main() -> None:
    with SessionLocal() as session:
        for plan_id, answers in DEMO_PLANS.items():
            inp = PlanInput(**answers)
            row = session.get(Plan, plan_id) or Plan(id=plan_id)
            row.input_json = inp.model_dump(mode="json")
            row.result_json = generate_plan(inp).model_dump(mode="json")
            row.engine_version = ENGINE_VERSION
            session.merge(row)
            print(f"demo plan {plan_id}: {inp.business_type}")
        session.commit()


if __name__ == "__main__":
    main()
