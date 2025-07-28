"""
Инициализация телеграм-бота Fixed Gear Perm.
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .config import BOT_TOKEN, logger

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Логируем только если файл импортируется, а не запускается напрямую
if __name__ != "__main__":
    logger.info("Бот и диспетчер инициализированы") 