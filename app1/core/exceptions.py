"""Exception hierarchy for the new application."""

from fastapi import HTTPException, status


class AppError(HTTPException):
    """Base HTTP exception for the new application stack."""

    def __init__(self, status_code: int = status.HTTP_400_BAD_REQUEST, detail: str = "App error") -> None:
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppError):
    """Raised when a requested entity cannot be found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class ConflictError(AppError):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail)


class UnauthorizedError(AppError):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


__all__ = ["AppError", "NotFoundError", "ConflictError", "UnauthorizedError"]
