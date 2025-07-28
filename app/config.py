"""
Конфигурация для телеграм-бота объявлений Fixed Gear Perm.
"""

import os
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MODERATION_CHAT_ID = os.getenv('MODERATION_CHAT_ID')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Проверка наличия необходимых переменных окружения
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

if not MODERATION_CHAT_ID:
    logger.warning("MODERATION_CHAT_ID не найден в .env файле")

if not CHANNEL_ID:
    logger.warning("CHANNEL_ID не найден в .env файле")

# Экспортируем все переменные
__all__ = ['BOT_TOKEN', 'MODERATION_CHAT_ID', 'CHANNEL_ID', 'logger'] 