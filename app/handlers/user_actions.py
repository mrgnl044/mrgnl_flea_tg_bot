"""
Обработчики действий пользователя для телеграм-бота объявлений Fixed Gear Perm.
"""

import logging
from aiogram import types

from ..bot import bot
from ..config import CHANNEL_ID
from ..keyboards import get_error_keyboard
from ..database import db

logger = logging.getLogger(__name__)

def register_handlers(dp):
    """
    Регистрирует все обработчики модуля
    
    :param dp: Диспетчер
    """
    # Обработчик кнопки "Продано"
    dp.callback_query.register(mark_as_sold, lambda c: c.data.startswith("sold_"))

async def mark_as_sold(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Товар обрёл нового владельца"
    
    :param callback: Обратный вызов
    """
    await callback.answer()
    
    # Извлекаем ID сообщения в канале из callback_data
    message_id = int(callback.data.split("_")[1])
    
    # Находим объявление в базе данных по ID сообщения в канале
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM published_ads 
            WHERE channel_message_id = ? AND status = 'active'
        """, (message_id,))
        row = cursor.fetchone()
        
        if not row:
            await callback.message.edit_text(
                "❌ <b>Объявление не найдено или уже продано.</b>",
                reply_markup=None,
                parse_mode="HTML"
            )
            return
        
        ad_id = row['id']
    
    try:
        # Простой и надежный способ: получаем сообщение через forward_message
        try:
            # Пересылаем сообщение пользователю (disable_notification=True чтобы не спамить)
            forwarded_msg = await bot.forward_message(
                chat_id=callback.from_user.id,
                from_chat_id=CHANNEL_ID,
                message_id=message_id,
                disable_notification=True
            )
            
            # Получаем текущую подпись
            current_caption = forwarded_msg.caption or ""
            
            # Проверяем, не помечено ли уже как продано
            if "🔴 ОБРЕЛО НОВОГО ВЛАДЕЛЬЦА" in current_caption:
                # Удаляем пересланное сообщение
                await bot.delete_message(
                    chat_id=callback.from_user.id,
                    message_id=forwarded_msg.message_id
                )
                await callback.message.edit_text(
                    "ℹ️ <i>Уже помечено как продано.</i>",
                    reply_markup=None,
                    parse_mode="HTML"
                )
                return
            
            # Удаляем пересланное сообщение у пользователя
            await bot.delete_message(
                chat_id=callback.from_user.id,
                message_id=forwarded_msg.message_id
            )
            
            # Добавляем метку ПРОДАНО
            new_caption = f"{current_caption}\n\n🔴 ОБРЕЛО НОВОГО ВЛАДЕЛЬЦА"
            
            await bot.edit_message_caption(
                chat_id=CHANNEL_ID,
                message_id=message_id,
                caption=new_caption,
                parse_mode="HTML"
            )
            
            # Отправляем подтверждение пользователю
            await callback.message.edit_text(
                "🎉 <b>Поздравляем с продажей!</b>\n\n"
                "<i>Объявление помечено как</i> <u>«Продано»</u>.",
                reply_markup=None,
                parse_mode="HTML"
            )
            
            # Обновляем статус в базе данных
            db.mark_ad_as_sold(ad_id, callback.from_user.id)
            
            logger.info(f"Объявление {ad_id} (сообщение {message_id}) помечено как продано пользователем {callback.from_user.id}")
            
        except Exception as forward_error:
            logger.error(f"Ошибка при получении сообщения через forward: {forward_error}")
            
            # Fallback: просто добавляем метку без получения текущего текста
            try:
                await bot.edit_message_caption(
                    chat_id=CHANNEL_ID,
                    message_id=message_id,
                    caption="🔴 ОБРЕЛО НОВОГО ВЛАДЕЛЬЦА",
                    parse_mode="HTML"
                )
                
                await callback.message.edit_text(
                    "🎉 <b>Поздравляем с продажей!</b>\n\n"
                    "<i>Объявление помечено как</i> <u>«Продано»</u>.",
                    reply_markup=None,
                    parse_mode="HTML"
                )
                
                # Обновляем статус в базе данных
                db.mark_ad_as_sold(ad_id, callback.from_user.id)
                
                logger.info(f"Объявление {ad_id} (сообщение {message_id}) помечено как продано (fallback)")
                
            except Exception as fallback_error:
                logger.error(f"Ошибка при fallback обновлении {message_id}: {fallback_error}")
                await callback.message.reply(
                    "⚠️ <b>Ошибка при обновлении статуса.</b>\n<i>Попробуй позже или обратись к администратору.</i>",
                    reply_markup=get_error_keyboard(),
                    parse_mode="HTML"
                )
    
    except Exception as e:
        logger.error(f"Критическая ошибка при обновлении статуса объявления: {e}")
        await callback.message.reply(
            "❌ <b>Произошла ошибка.</b>\n<i>Обратись к администратору.</i>",
            reply_markup=get_error_keyboard(),
            parse_mode="HTML"
        ) 