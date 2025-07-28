"""
Главный файл телеграм-бота объявлений Fixed Gear Perm.
"""

import asyncio
import logging

from app.bot import bot, dp
from app.handlers import register_all_handlers
from app.config import logger

async def main():
    """
    Главная функция запуска бота
    """
    logger.info("Запуск бота Fixed Gear Perm")
    
    # Регистрируем все обработчики
    register_all_handlers(dp)
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 