"""
Состояния FSM для телеграм-бота объявлений marginal_bot.
"""

from aiogram.fsm.state import State, StatesGroup

class AdStates(StatesGroup):
    """Состояния для создания объявления"""
    waiting_for_photos = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()
    review = State() 