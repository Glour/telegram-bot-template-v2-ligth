"""Common keyboard builders."""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build main menu inline keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Профиль", callback_data="profile")
    builder.button(text="Помощь", callback_data="help")
    builder.adjust(2)
    return builder.as_markup()
