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


class EventType(str, Enum):
    """Analytics event types."""

    USER_REGISTERED = "user_registered"
    USER_BLOCKED_BOT = "user_blocked_bot"
    USER_UNBLOCKED_BOT = "user_unblocked_bot"
    COMMAND_EXECUTED = "command_executed"
    MESSAGE_SENT = "message_sent"
    BUTTON_CLICKED = "button_clicked"
    ERROR_OCCURRED = "error_occurred"
