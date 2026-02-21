"""Prometheus metrics for bot monitoring."""
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from config.settings.base import get_settings

# Bot message metrics
bot_messages_total = Counter(
    "bot_messages_total",
    "Total messages processed by bot",
    ["handler", "status"],
)

bot_commands_total = Counter(
    "bot_commands_total",
    "Total commands executed",
    ["command"],
)

bot_errors_total = Counter(
    "bot_errors_total",
    "Total errors occurred",
    ["error_type"],
)

# Response time metrics
bot_response_time = Histogram(
    "bot_response_time_seconds",
    "Time spent processing message",
    ["handler"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# User metrics
bot_active_users = Gauge(
    "bot_active_users",
    "Number of active users",
    ["period"],
)

bot_total_users = Gauge(
    "bot_total_users",
    "Total number of users",
)

# Database metrics
database_connections = Gauge(
    "database_connections_active",
    "Active database connections",
)

database_query_duration = Histogram(
    "database_query_duration_seconds",
    "Database query execution time",
    ["operation"],
)


def start_metrics_server() -> None:
    """Start Prometheus metrics HTTP server."""
    settings = get_settings()

    if settings.metrics.enabled:
        start_http_server(settings.metrics.port)
        from infrastructure.monitoring.logging import get_logger

        logger = get_logger(__name__)
        logger.info(
            "metrics_server_started",
            port=settings.metrics.port,
        )
