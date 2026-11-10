import re
from collections.abc import Sequence

from sqlalchemy import RowMapping, func, or_, select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models.employee import Employee

# Explicit column projection avoids fetching unnecessary fields if columns are added later.
EMPLOYEE_COLUMNS = (
    Employee.id,
    Employee.name,
    Employee.email,
    Employee.department,
    Employee.designation,
    Employee.date_of_joining,
)

_ALNUM_SPACE_RE = re.compile(r"^[A-Za-z0-9\s]+$")
_MIN_FULLTEXT_TOKEN_LEN = 3


def _escape_like(value: str) -> str:
    """Escape SQL LIKE wildcards so literal %, _, and \\ characters are matched safely."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class EmployeeRepository:
    """Data-access layer for employee records. Contains only database queries."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _build_search_filter(self, search: str) -> ColumnElement[bool]:
        """Build an index-friendly filter across employee name and department.

        - On MySQL, multi-character alphanumeric tokens (>= 3 chars) use the FULLTEXT index
          in boolean prefix mode so both first and last names/words match in O(log N).
        - Short tokens (< 3 chars, such as 'HR' or 'IT') or special-character queries fall back
          to B-Tree prefix LIKE ('term%') without wrapping columns in LOWER(), preserving index use.
        """
        dialect = self.db.get_bind().dialect.name
        escaped = _escape_like(search)

        if dialect == "mysql" and _ALNUM_SPACE_RE.fullmatch(search):
            tokens = search.split()
            if tokens and all(len(token) >= _MIN_FULLTEXT_TOKEN_LEN for token in tokens):
                boolean_query = " ".join(f"+{token}*" for token in tokens)
                return text(
                    "MATCH(employees.name, employees.department) "
                    "AGAINST(:ft_query IN BOOLEAN MODE)"
                ).bindparams(ft_query=boolean_query)

        if dialect == "mysql":
            prefix = f"{escaped}%"
            return or_(
                Employee.name.like(prefix, escape="\\"),
                Employee.department.like(prefix, escape="\\"),
            )

        # Fallback for SQLite in unit tests
        prefix = f"{escaped}%"
        word_prefix = f"% {escaped}%"
        return or_(
            Employee.name.ilike(prefix, escape="\\"),
            Employee.name.ilike(word_prefix, escape="\\"),
            Employee.department.ilike(prefix, escape="\\"),
            Employee.department.ilike(word_prefix, escape="\\"),
        )

    def search_employees(
        self,
        search: str | None,
        limit: int,
        offset: int,
    ) -> tuple[Sequence[RowMapping], int]:
        """Return paginated matching employee rows and total matching row count."""
        filters = [self._build_search_filter(search)] if search is not None else []

        count_stmt = select(func.count(Employee.id)).where(*filters)
        total = int(self.db.execute(count_stmt).scalar_one())

        if total == 0 or offset >= total:
            return [], total

        data_stmt = (
            select(*EMPLOYEE_COLUMNS)
            .where(*filters)
            .order_by(Employee.name.asc(), Employee.id.asc())
            .limit(limit)
            .offset(offset)
        )
        rows = self.db.execute(data_stmt).mappings().all()
        return rows, total

