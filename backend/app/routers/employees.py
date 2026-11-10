from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.employee_repo import EmployeeRepository
from app.schemas.employee import EmployeeListResponse, ErrorResponse
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    """Wire EmployeeRepository into EmployeeService for each request."""
    return EmployeeService(EmployeeRepository(db))


@router.get(
    "",
    response_model=EmployeeListResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Empty or invalid search query"},
        422: {"model": ErrorResponse, "description": "Invalid query parameter bounds/types"},
        503: {"model": ErrorResponse, "description": "Database connection failure"},
    },
)
def list_employees(
    search: str | None = Query(
        default=None,
        description="Search employees by name or department (omit to list all paginated).",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of employees to return per page (1-100).",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of matching records to skip for pagination.",
    ),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeListResponse:
    """Thin HTTP route handler delegating search logic to EmployeeService."""
    return service.search_employees(search=search, limit=limit, offset=offset)

