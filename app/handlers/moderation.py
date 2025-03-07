"""
Обработчики модерации объявлений для телеграм-бота объявлений marginal_bot.
"""

import logging
from aiogram import types

from ..bot import bot, dp
from ..config import CHANNEL_ID
from ..utils import create_ad_text, create_media_group
from ..keyboards import get_sold_keyboard, get_create_new_ad_keyboard

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
    
    # Извлекаем ID пользователя из callback_data
    user_id = callback.data.split("_")[1]
    
    # Получаем данные объявления из хранилища
    ad_data = await dp.storage.get_data(key=f"ad_{user_id}")
    
    if not ad_data:
        await callback.message.reply("🧩 Досадное недоразумение: данные об объявлении бесследно исчезли из системы! Возможно, автор передумал или произошла техническая ошибка.")
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
            chat_id=int(user_id),
            text=(
                "✅ <b>Отличные новости! Ваше объявление одобрено!</b>\n\n"
                "Оно уже опубликовано в нашем канале и теперь доступно всем участникам сообщества. "
                "Когда товар будет продан, не забудьте отметить это, нажав на кнопку «Товар обрёл нового владельца» ниже."
            ),
            reply_markup=get_sold_keyboard(channel_msg_id),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
    
    # Обновляем сообщение в чате модерации
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ ОДОБРЕНО модератором {callback.from_user.first_name}",
        reply_markup=None
    )
    
    # Удаляем данные объявления из хранилища
    await dp.storage.set_data(key=f"ad_{user_id}", data={})

async def reject_ad(callback: types.CallbackQuery):
    """
    Обработчик отклонения объявления модератором
    
    :param callback: Обратный вызов
    """
    await callback.answer()
    
    # Извлекаем ID пользователя из callback_data
    user_id = callback.data.split("_")[1]
    
    # Получаем данные объявления из хранилища
    ad_data = await dp.storage.get_data(key=f"ad_{user_id}")
    
    if not ad_data:
        await callback.message.reply("🧩 К сожалению, данные объявления не найдены. Возможно, запись была удалена из системы.")
        return
    
    # Отправляем уведомление автору объявления
    try:
        await bot.send_message(
            chat_id=int(user_id),
            text=(
                "⚠️ <b>Ваше объявление не прошло модерацию</b>\n\n"
                "К сожалению, модераторы отклонили ваше объявление. Возможные причины: недостаточное качество фотографий, неполное описание, некорректная цена или другие несоответствия правилам сообщества.\n\n"
                "Вы можете создать новое объявление, улучшив качество материалов и информации. Удачи в следующей попытке!"
            ),
            reply_markup=get_create_new_ad_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
    
    # Обновляем сообщение в чате модерации
    await callback.message.edit_text(
        f"{callback.message.text}\n\n❌ ОТКЛОНЕНО модератором {callback.from_user.first_name}",
        reply_markup=None
    )
    
    # Удаляем данные объявления из хранилища
    await dp.storage.set_data(key=f"ad_{user_id}", data={}) 