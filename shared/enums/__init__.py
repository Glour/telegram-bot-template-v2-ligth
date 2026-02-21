"""Application enums."""
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""

    USER = "user"
    PREMIUM = "premium"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User status enumeration."""

    ACTIVE = "active"
    BLOCKED = "blocked"
    BANNED = "banned"
    DELETED = "deleted"


class Language(str, Enum):
    """Supported languages."""

    RU = "ru"
    EN = "en"
    UK = "uk"
