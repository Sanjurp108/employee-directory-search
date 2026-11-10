import logging

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.db.session import get_db
from app.routers.employees import router as employees_router
from app.schemas.employee import ErrorResponse

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Employee Directory Search System API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Convert domain exceptions into structured HTTP error responses."""
    payload = ErrorResponse(detail=exc.message, error_code=exc.error_code)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Format FastAPI query validation errors into consistent ErrorResponse payloads."""
    first_error = exc.errors()[0] if exc.errors() else {}
    location = ".".join(str(part) for part in first_error.get("loc", []) if part != "query")
    message = first_error.get("msg", "Invalid request parameters.")
    detail = f"Invalid parameter '{location}': {message}" if location else message
    payload = ErrorResponse(detail=detail, error_code="VALIDATION_ERROR")
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Return a safe 503 response on database connection or query failures."""
    logger.exception("Database error encountered while handling request: %s", exc)
    payload = ErrorResponse(
        detail="Database is temporarily unavailable. Please try again later.",
        error_code="DATABASE_UNAVAILABLE",
    )
    return JSONResponse(status_code=503, content=payload.model_dump())


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Check API responsiveness and live database connectivity."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


app.include_router(employees_router)

