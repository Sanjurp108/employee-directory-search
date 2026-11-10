from app.core.exceptions import InvalidQueryError
from app.repositories.employee_repo import EmployeeRepository
from app.schemas.employee import EmployeeListResponse, EmployeeOut

MAX_SEARCH_LENGTH = 100


class EmployeeService:
    """Business logic layer for employee directory operations."""

    def __init__(self, repository: EmployeeRepository) -> None:
        self.repository = repository

    def search_employees(
        self,
        search: str | None,
        limit: int,
        offset: int,
    ) -> EmployeeListResponse:
        """Normalize and validate search parameters, then return paginated employee matches."""
        cleaned_search: str | None = None
        if search is not None:
            cleaned_search = search.strip()
            if not cleaned_search:
                raise InvalidQueryError("Search query cannot be empty or whitespace.")
            if len(cleaned_search) > MAX_SEARCH_LENGTH:
                raise InvalidQueryError(
                    f"Search query must be {MAX_SEARCH_LENGTH} characters or fewer."
                )

        rows, total = self.repository.search_employees(
            search=cleaned_search,
            limit=limit,
            offset=offset,
        )
        items = [EmployeeOut.model_validate(row) for row in rows]
        return EmployeeListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            search=cleaned_search,
        )

