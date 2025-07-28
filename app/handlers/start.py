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
        "🎭 <b>Приветствую, ценитель всего велосипедного – от рам до звонков!</b>\n\n"
        "Добро пожаловать в <b>Fixed Gear Perm</b> – эксклюзивную галерею, где любая велотематика обретает ценность: будь то целый велосипед, редкая запчасть или тот странный аксессуар, чье предназначение вы уже забыли.\n"
        "Нажмите кнопку ниже, чтобы представить миру своё сокровище. В конце концов, ваше старое седло может стать чьим-то идеальным дополнением к велоколлекции, а та горка гаек и болтов в углу гаража – настоящим спасением для кого-то с сорванной резьбой.",
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    ) 