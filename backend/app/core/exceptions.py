class AppError(Exception):
    """Base application exception mapped to HTTP responses at the API boundary."""

    def __init__(self, message: str, status_code: int = 400, error_code: str = "APP_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class InvalidQueryError(AppError):
    """Raised when search or pagination input fails domain validation."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=400, error_code="INVALID_QUERY")

