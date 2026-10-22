"""LaunchWise API entry point. All routes live under /api (nginx proxies /api/ here)."""

import logging

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import APP_VERSION
from app.db import db_is_alive
from app.routers import examples, options, plans

log = logging.getLogger("launchwise")

app = FastAPI(
    title="LaunchWise API",
    version=APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict:
    # Never fails: a DB problem is reported as "error" instead of a 500.
    return {"status": "ok", "db": "ok" if db_is_alive() else "error", "version": APP_VERSION}


api.include_router(options.router)
api.include_router(plans.router)
api.include_router(examples.router)
app.include_router(api)


FRIENDLY_FIELD_ERRORS = {
    "plan_id": "Plan id must be 10 lowercase letters or digits.",
}


@app.exception_handler(RequestValidationError)
def readable_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """422 with one readable message per field, e.g. {"field": "languages", "message": "..."}."""
    errors = []
    for err in exc.errors():
        if err["type"] == "json_invalid":
            errors.append({"field": "body", "message": "The request body is not valid JSON."})
            continue
        loc = [str(part) for part in err["loc"] if part not in ("body", "query", "path")]
        field = ".".join(loc) or "body"
        message = FRIENDLY_FIELD_ERRORS.get(field, err["msg"].removeprefix("Value error, "))
        errors.append({"field": field, "message": message})
    return JSONResponse(status_code=422, content={"detail": "Please check your answers.", "errors": errors})


@app.exception_handler(Exception)
def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Safety net: log the details, never send a stack trace to the client."""
    log.exception("Unexpected error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on our side. Please try again."})


@app.exception_handler(SQLAlchemyError)
def database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    log.exception("Database error on %s", request.url.path)
    return JSONResponse(status_code=503, content={"detail": "The database is temporarily unavailable. Please try again."})
