"""
Обработчики модерации объявлений для телеграм-бота объявлений Fixed Gear Perm.
"""

import logging
from aiogram import types

from ..bot import bot, dp
from ..config import CHANNEL_ID
from ..utils import create_ad_text, create_media_group
from ..keyboards import get_sold_keyboard, get_create_new_ad_keyboard
from ..database import db

logger = logging.getLogger(__name__)

def register_handlers(dp):
    """
    Регистрирует все обработчики модуля
    
    :param dp: Диспетчер
    """
    # Обработчики модерации
    dp.callback_query.register(approve_ad, lambda c: c.data.startswith("approve_"))
    dp.callback_query.register(reject_ad, lambda c: c.data.startswith("reject_"))

async def approve_ad(callback: types.CallbackQuery):
    """
    Обработчик одобрения объявления модератором
    
    :param callback: Обратный вызов
    """
    await callback.answer()
    
    # Извлекаем ID объявления из callback_data
    ad_id = int(callback.data.split("_")[1])
    
    # Получаем данные объявления из базы данных
    ad_data = db.get_moderation_ad(ad_id)
    
    if not ad_data:
        await callback.message.reply("Данные объявления не найдены!")
        return
    
    # Формируем текст объявления для публикации в канале
    post_text = create_ad_text(ad_data)
    
    channel_msg_id = None
    
    # Публикуем объявление в канале
    photos = ad_data['photos']
    if photos:
        # Создаем группу медиа для публикации в канале
        media_group = create_media_group(photos, post_text, "HTML")
        
        # Отправляем группу фотографий в канал
        channel_msgs = await bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
        channel_msg_id = channel_msgs[0].message_id
    
    # Отправляем уведомление автору объявления
    try:
        await bot.send_message(
            chat_id=ad_data['user_id'],
            text=(
                "✅ <b>Объявление одобрено!</b>\n\n"
                "🎉 <i>Оно опубликовано в канале.</i> Когда продашь - нажми <u>«Продано»</u>"
            ),
            reply_markup=get_sold_keyboard(channel_msg_id),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление пользователю {ad_data['user_id']}: {e}")
    
    # Обновляем сообщение в чате модерации
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ ОДОБРЕНО",
        reply_markup=None
    )
    
    # Сохраняем объявление в базу данных как опубликованное
    published_ad_id = db.save_published_ad(
        ad_data['user_id'], 
        ad_data, 
        channel_msg_id, 
        int(CHANNEL_ID)
    )
    
    # Обновляем статус модерации
    db.update_moderation_status(
        ad_id, 
        'approved', 
        callback.from_user.id,
        callback.message.message_id,
        callback.message.chat.id
    )

async def reject_ad(callback: types.CallbackQuery):
    """
    Обработчик отклонения объявления модератором
    
    :param callback: Обратный вызов
    """
    await callback.answer()
    
    # Извлекаем ID объявления из callback_data
    ad_id = int(callback.data.split("_")[1])
    
    # Получаем данные объявления из базы данных
    ad_data = db.get_moderation_ad(ad_id)
    
    if not ad_data:
        await callback.message.reply("Данные объявления не найдены.")
        return
    
    # Отправляем уведомление автору объявления
    try:
        await bot.send_message(
            chat_id=ad_data['user_id'],
            text=(
                "❌ <b>Объявление отклонено</b>\n\n"
                "🔄 <i>Создай новое объявление с лучшими фото и описанием.</i>"
            ),
            reply_markup=get_create_new_ad_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление пользователю {ad_data['user_id']}: {e}")
    
    # Обновляем сообщение в чате модерации
    await callback.message.edit_text(
        f"{callback.message.text}\n\n❌ ОТКЛОНЕНО",
        reply_markup=None
    )
    
    # Обновляем статус модерации
    db.update_moderation_status(
        ad_id, 
        'rejected', 
        callback.from_user.id,
        callback.message.message_id,
        callback.message.chat.id
    ) 