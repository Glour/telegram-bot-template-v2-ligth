"""Example FSM states."""
from aiogram.fsm.state import State, StatesGroup


class ExampleForm(StatesGroup):
    """Example form with multiple steps."""

    waiting_for_name = State()
    waiting_for_description = State()
    confirmation = State()
