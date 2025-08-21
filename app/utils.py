"""
Вспомогательные функции для телеграм-бота
"""

import logging
from aiogram.types import InputMediaPhoto

logger = logging.getLogger(__name__)

def get_category_name(category_code: str) -> str:
    """
    Получает название категории по коду
    
    :param category_code: Код категории
    :return: Название категории с хештегом
    """
    categories = {
        "sell": "#продам",
        "buy": "#куплю", 
        "trade": "#обмен",
        "rent": "#аренда",
        "free": "#даром",
        "service": "#услуги",
        "race": "#гонка",
        "event": "#мероприятие"
    }
    return categories.get(category_code, "#другое")

def format_price(price_text: str) -> str:
    """
    Форматирует цену с разделителями тысяч
    
    :param price_text: Текст с ценой
    :return: Отформатированная цена
    """
    # Проверяем на "Даром"
    if price_text.strip().lower() in ["даром", "бесплатно", "free"]:
        return "Даром"
    
    try:
        price = int(price_text.replace(" ", ""))
        if price <= 0:
            raise ValueError("Отрицательная цена")
        return f"{price:,}".replace(",", " ") + " ₽"
    except ValueError:
        raise ValueError("Неверный формат цены")

def get_user_mention(user):
    """
    Получает упоминание пользователя
    
    :param user: Пользователь Telegram
    :return: Упоминание пользователя
    """
    return f"@{user.username}" if user.username else f"tg://user?id={user.id}"

def get_user_display(user):
    """
    Получает отображаемое имя пользователя
    
    :param user: Пользователь Telegram
    :return: Отображаемое имя пользователя
    """
    return f"@{user.username}" if user.username else f"{user.first_name} (нет @username!)"

def create_ad_text(data, is_moderation=False):
    """
    Создает текст объявления
    
    :param data: Данные объявления
    :param is_moderation: Флаг, указывающий на создание текста для модерации
    :return: Текст объявления
    """
    # Получаем категорию
    category = get_category_name(data.get('category', 'sell'))
    
    text = (
        f"{category}\n"
        f"🚲 <b>{data['title']}</b>\n\n"
        f"📌 {data['description']}\n"
        f"💰 Цена: {data['price']}\n"
        f"📞 Контакт: {data['user_display']}\n\n"
    )
    
    if is_moderation:
        text += f"От пользователя: {data['user_mention']}"
    else:
        text += "Создать объяву: @fgp_mrktbot"
    
    return text

def create_media_group(photos, caption=None, parse_mode=None):
    """
    Создает медиа-группу для отправки фотографий
    
    :param photos: Список ID фотографий
    :param caption: Подпись к первой фотографии
    :param parse_mode: Режим форматирования текста
    :return: Медиа-группа
    """
    media_group = []
    for i, photo_id in enumerate(photos):
        if i == 0 and caption:
            media_group.append(InputMediaPhoto(media=photo_id, caption=caption, parse_mode=parse_mode))
        else:
            media_group.append(InputMediaPhoto(media=photo_id))
    return media_group 