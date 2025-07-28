"""
Клавиатуры для телеграм-бота объявлений Fixed Gear Perm.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_start_keyboard():
    """Клавиатура для стартового сообщения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚲 Выставить велотовар на обозрение", callback_data="create_ad")]
    ])

def get_photos_done_keyboard():
    """Клавиатура для завершения загрузки фотографий"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Двигаемся дальше", callback_data="photos_done")]
    ])

def get_review_keyboard():
    """Клавиатура для предпросмотра объявления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить мой лот на модерацию", callback_data="send_to_moderation")],
        [InlineKeyboardButton(text="🔄 Неудачный ракурс. Начнём заново", callback_data="create_ad")]
    ])

def get_moderation_keyboard(user_id):
    """Клавиатура для модерации объявления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ В витрину магазина", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Вернуть в коробку", callback_data=f"reject_{user_id}")
        ]
    ])

def get_sold_keyboard(channel_msg_id):
    """Клавиатура с кнопкой 'Продано'"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 Товар обрёл нового владельца", callback_data=f"sold_{channel_msg_id}")]
    ])

def get_create_new_ad_keyboard():
    """Клавиатура для создания нового объявления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚲 Продать ещё что-нибудь из велозаначки", callback_data="create_ad")]
    ]) 