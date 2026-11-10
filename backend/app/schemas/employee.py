from datetime import date

from pydantic import BaseModel, ConfigDict


class EmployeeOut(BaseModel):
    """Serialized employee record returned by the directory API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    department: str
    designation: str
    date_of_joining: date


class EmployeeListResponse(BaseModel):
    """Paginated employee search response."""

    items: list[EmployeeOut]
    total: int
    limit: int
    offset: int
    search: str | None = None


class ErrorResponse(BaseModel):
    """Consistent error payload returned across API error responses."""

    detail: str
    error_code: str

