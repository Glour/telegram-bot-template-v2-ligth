"""Application exceptions."""
from shared.exceptions.base import (
    AlreadyExistsError,
    AppException,
    DatabaseError,
    ExternalServiceError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

__all__ = [
    "AppException",
    "ValidationError",
    "NotFoundError",
    "AlreadyExistsError",
    "PermissionDeniedError",
    "ExternalServiceError",
    "DatabaseError",
]
