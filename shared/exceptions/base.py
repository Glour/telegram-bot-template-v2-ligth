"""Base exception classes."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str | None = None, details: dict | None = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error exception."""

    pass


class NotFoundError(AppException):
    """Resource not found exception."""

    pass


class AlreadyExistsError(AppException):
    """Resource already exists exception."""

    pass


class PermissionDeniedError(AppException):
    """Permission denied exception."""

    pass


class ExternalServiceError(AppException):
    """External service error exception."""

    pass


class DatabaseError(AppException):
    """Database operation error exception."""

    pass
