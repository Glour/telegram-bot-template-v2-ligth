"""SQLAdmin view for User model."""
from sqladmin import ModelView

from infrastructure.database.models.users import User


class UserAdmin(ModelView, model=User):
    """Admin view for User model."""

    # Displayed name
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    # List page
    column_list = [
        User.id,
        User.telegram_id,
        User.username,
        User.first_name,
        User.language,
        User.role,
        User.status,
        User.created_at,
        User.last_activity_at,
    ]

    column_sortable_list = [
        User.id,
        User.telegram_id,
        User.username,
        User.created_at,
        User.last_activity_at,
    ]

    column_searchable_list = [
        User.username,
        User.first_name,
        User.last_name,
    ]

    column_filters = [
        User.role,
        User.status,
        User.language,
        User.created_at,
    ]

    # Detail page
    column_details_list = [
        User.id,
        User.telegram_id,
        User.username,
        User.first_name,
        User.last_name,
        User.language,
        User.role,
        User.status,
        User.referrer_id,
        User.total_messages,
        User.last_activity_at,
        User.created_at,
        User.updated_at,
    ]

    # Form
    form_columns = [
        User.telegram_id,
        User.username,
        User.first_name,
        User.last_name,
        User.language,
        User.role,
        User.status,
        User.referrer_id,
    ]

    # Pagination
    page_size = 50
    page_size_options = [25, 50, 100, 200]

    # Export
    can_export = True
    export_types = ["csv", "json"]

    # Actions
    can_create = False  # Users created only via bot
    can_edit = True
    can_delete = True
    can_view_details = True

    # Custom labels
    column_labels = {
        User.id: "ID",
        User.telegram_id: "Telegram ID",
        User.username: "Username",
        User.first_name: "First Name",
        User.last_name: "Last Name",
        User.language: "Language",
        User.role: "Role",
        User.status: "Status",
        User.referrer_id: "Referrer ID",
        User.total_messages: "Total Messages",
        User.last_activity_at: "Last Activity",
        User.created_at: "Created At",
        User.updated_at: "Updated At",
    }

    # Descriptions
    column_descriptions = {
        User.telegram_id: "Unique Telegram user ID",
        User.role: "User role: user, premium, moderator, admin",
        User.status: "User status: active, blocked, banned, deleted",
    }
