"""
Обработчики команды /start для телеграм-бота объявлений Fixed Gear Perm.
"""

from aiogram import types
from aiogram.filters import Command

from ..bot import bot
from ..keyboards import get_start_keyboard

def register_handlers(dp):
    """
    Регистрирует все обработчики модуля
    
    :param dp: Диспетчер
    """
    dp.message.register(cmd_start, Command("start"))

async def cmd_start(message: types.Message):
    """
    Обработчик команды /start
    
    :param message: Сообщение
    """
    await message.answer(
        "🎭 <b>Привет!</b>\n\n"
        "Добро пожаловать в <b>FGP_MIXEDBARAHOLKA</b>!\n\n"
        "<i>Здесь можно продать вещи и анонсировать события.</i>",
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    ) 