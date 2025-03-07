"""
Обработчики действий пользователя для телеграм-бота объявлений marginal_bot.
"""

import logging
from aiogram import types

from ..bot import bot
from ..config import CHANNEL_ID

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
    
    try:
        # Флаг успешного добавления метки ПРОДАНО
        success = False
        
        # СПОСОБ 1: Пробуем скопировать сообщение, чтобы получить его текущий текст
        try:
            # Сначала попробуем скопировать сообщение, чтобы узнать его содержимое
            copied_msg = await bot.copy_message(
                chat_id=callback.from_user.id,
                from_chat_id=CHANNEL_ID,
                message_id=message_id,
                disable_notification=True
            )
            
            # Сохраняем текст
            current_text = copied_msg.caption or ""
            
            # Удаляем скопированное сообщение у пользователя
            await bot.delete_message(
                chat_id=callback.from_user.id,
                message_id=copied_msg.message_id
            )
            
            # Обновляем сообщение в канале, сохраняя текст и добавляя метку ПРОДАНО
            await bot.edit_message_caption(
                chat_id=CHANNEL_ID,
                message_id=message_id,
                caption=f"{current_text}\n\n🔴 ОБРЕЛО НОВОГО ВЛАДЕЛЬЦА",
                parse_mode="HTML"
            )
            success = True
        except Exception as copy_error:
            logger.error(f"Ошибка при копировании сообщения: {copy_error}")
        
        # СПОСОБ 2: Если первый способ не сработал, попробуем получить сообщение через пересылку
        if not success:
            try:
                # Пересылаем сообщение из канала себе, чтобы получить его содержимое
                forwarded_msg = await bot.forward_message(
                    chat_id=callback.from_user.id,
                    from_chat_id=CHANNEL_ID,
                    message_id=message_id,
                    disable_notification=True
                )
                
                # Получаем текущую подпись
                current_caption = forwarded_msg.caption or ""
                
                # Удаляем пересланное сообщение у пользователя
                await bot.delete_message(
                    chat_id=callback.from_user.id,
                    message_id=forwarded_msg.message_id
                )
                
                # Добавляем метку ПРОДАНО
                await bot.edit_message_caption(
                    chat_id=CHANNEL_ID,
                    message_id=message_id,
                    caption=f"{current_caption}\n\n🔴 ОБРЕЛО НОВОГО ВЛАДЕЛЬЦА",
                    parse_mode="HTML"
                )
                success = True
            except Exception as forward_error:
                logger.error(f"Ошибка при пересылке сообщения: {forward_error}")
        
        # СПОСОБ 3: Если и второй способ не сработал, попробуем получить текст через edit_message_caption
        if not success:
            try:
                # Делаем запрос edit_message_caption без изменения текста,
                # чтобы получить текущий текст
                result = await bot.edit_message_caption(
                    chat_id=CHANNEL_ID,
                    message_id=message_id,
                    caption=None  # не меняем подпись
                )
                
                # Получаем текущую подпись
                current_caption = result.caption or ""
                
                # Добавляем метку ПРОДАНО
                await bot.edit_message_caption(
                    chat_id=CHANNEL_ID,
                    message_id=message_id,
                    caption=f"{current_caption}\n\n🔴 ОБРЕЛО НОВОГО ВЛАДЕЛЬЦА",
                    parse_mode="HTML"
                )
                success = True
            except Exception as edit_error:
                logger.error(f"Ошибка при получении текста через edit_message_caption: {edit_error}")
        
        # Если все способы не сработали, сообщаем об ошибке, но НЕ заменяем текст
        if not success:
            logger.error("Все методы получения текста объявления не сработали!")
            await callback.message.reply(
                "🔧 Произошла техническая ошибка при обновлении статуса объявления.\n\n"
                "Пожалуйста, попробуйте повторить действие позже или свяжитесь с администратором канала для ручного изменения статуса объявления."
            )
            return
        
        # Отправляем подтверждение пользователю
        await callback.message.edit_text(
            "🎊 <b>Поздравляем с успешной продажей!</b>\n\n"
            "Ваше объявление теперь помечено как «Продано». Благодарим за использование нашей площадки! Будем рады видеть вас снова, когда решите продать ещё что-нибудь из своей коллекции.",
            reply_markup=None,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса объявления: {e}")
        await callback.message.reply(
            "⚠️ К сожалению, произошла ошибка при изменении статуса объявления.\n\n"
            "Рекомендуем обратиться к администрации канала для решения этой проблемы."
        ) 