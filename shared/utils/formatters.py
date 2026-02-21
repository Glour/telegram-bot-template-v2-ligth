"""Utility functions for formatting data."""
from datetime import datetime


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(fmt)


def format_number(num: int | float, thousand_sep: str = " ") -> str:
    """Format number with thousand separator."""
    return f"{num:,}".replace(",", thousand_sep)


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate string to max length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def escape_markdown(text: str) -> str:
    """Escape Markdown special characters."""
    special_chars = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text
