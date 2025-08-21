"""
Клавиатуры для телеграм-бота объявлений Fixed Gear Perm.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_start_keyboard():
    """Клавиатура для стартового сообщения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚲 Создать объявление", callback_data="create_ad")]
    ])

def get_category_keyboard():
    """Клавиатура для выбора категории объявления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Продам", callback_data="category_sell"),
            InlineKeyboardButton(text="🛒 Куплю", callback_data="category_buy")
        ],
        [
            InlineKeyboardButton(text="🔄 Обмен", callback_data="category_trade"),
            InlineKeyboardButton(text="⏰ Аренда", callback_data="category_rent")
        ],
        [
            InlineKeyboardButton(text="🎁 Даром", callback_data="category_free"),
            InlineKeyboardButton(text="🔧 Услуги", callback_data="category_service")
        ],
        [
            InlineKeyboardButton(text="🏁 Гонка", callback_data="category_race"),
            InlineKeyboardButton(text="🎪 Мероприятие", callback_data="category_event")
        ]
    ])

def get_photos_done_keyboard():
    """Клавиатура для завершения загрузки фотографий"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Дальше", callback_data="photos_done")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="start_command")]
    ])

def get_review_keyboard():
    """Клавиатура для предпросмотра объявления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить на модерацию", callback_data="send_to_moderation")],
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="create_ad")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="start_command")]
    ])

def get_moderation_keyboard(ad_id):
    """Клавиатура для модерации объявления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{ad_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{ad_id}")
        ]
    ])

def get_sold_keyboard(channel_msg_id):
    """Клавиатура с кнопкой 'Продано'"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 Продано", callback_data=f"sold_{channel_msg_id}")]
    ])

def get_create_new_ad_keyboard():
    """Клавиатура для создания нового объявления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚲 Создать ещё", callback_data="create_ad")]
    ])

def get_error_keyboard():
    """Клавиатура для ошибок с кнопкой возврата в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="start_command")]
    ]) 