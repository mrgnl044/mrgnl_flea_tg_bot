"""
Обработчики создания объявления для телеграм-бота объявлений Fixed Gear Perm.
"""

from aiogram import types
from aiogram.fsm.context import FSMContext
import logging

from ..bot import bot, dp
from ..states import AdStates
from ..keyboards import get_category_keyboard, get_photos_done_keyboard, get_review_keyboard, get_moderation_keyboard, get_error_keyboard, get_start_keyboard, get_create_new_ad_keyboard
from ..utils import (
    format_price, get_user_mention, get_user_display, 
    create_ad_text, create_media_group, get_category_name
)
from ..config import MODERATION_CHAT_ID
from ..database import db

def register_handlers(dp):
    """
    Регистрирует обработчики создания объявления
    
    :param dp: Диспетчер
    """
    # Начало создания объявления
    dp.callback_query.register(create_ad, lambda c: c.data == "create_ad")
    
    # Обработка выбора категории
    dp.callback_query.register(process_category, lambda c: c.data.startswith("category_"))
    
    # Обработка фотографий
    dp.message.register(process_photo, AdStates.waiting_for_photos, lambda message: message.photo)
    dp.callback_query.register(photos_done, AdStates.waiting_for_photos, lambda c: c.data == "photos_done")
    
    # Обработка возврата в главное меню (глобальный обработчик)
    dp.callback_query.register(go_to_start, lambda c: c.data == "start_command")
    
    # Обработка заголовка, описания и цены
    dp.message.register(process_title, AdStates.waiting_for_title)
    dp.message.register(process_description, AdStates.waiting_for_description)
    dp.message.register(process_price, AdStates.waiting_for_price)
    
    # Отправка на модерацию
    dp.callback_query.register(send_to_moderation, AdStates.review, lambda c: c.data == "send_to_moderation")

async def create_ad(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Выставить велотовар на обозрение"
    
    :param callback: Обратный вызов
    :param state: Состояние FSM
    """
    await callback.answer()
    
    # Сбрасываем предыдущее состояние
    await state.clear()
    
    await callback.message.answer(
        "📋 <b>Выбери категорию</b>\n\n"
        "<i>Выбери подходящую категорию для твоего объявления:</i>",
        reply_markup=get_category_keyboard(),
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние ожидания выбора категории
    await state.set_state(AdStates.waiting_for_category)

async def process_category(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик выбора категории
    
    :param callback: Обратный вызов
    :param state: Состояние FSM
    """
    await callback.answer()
    
    # Извлекаем код категории из callback_data
    category_code = callback.data.split("_")[1]
    category_name = get_category_name(category_code)
    
    # Сохраняем категорию
    await state.update_data(category=category_code)
    
    # Создаем пустой список для фотографий
    await state.update_data(photos=[])
    
    await callback.message.answer(
        f"📸 <b>Загрузи фото</b>\n\n"
        f"Категория: <code>{category_name}</code>\n\n"
        "<i>Присылай фото по одному (до 3-х штук). Хорошие фото = быстрая продажа!</i>",
        reply_markup=get_photos_done_keyboard(),
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние ожидания фотографий
    await state.set_state(AdStates.waiting_for_photos)

async def process_photo(message: types.Message, state: FSMContext):
    """
    Обработчик фотографий
    
    :param message: Сообщение
    :param state: Состояние FSM
    """
    data = await state.get_data()
    photos = data.get("photos", [])
    
    # Проверяем, что у нас не больше 3-х фотографий
    if len(photos) >= 3:
        await message.answer("<b>Хватит фото!</b> 📸\n<i>Нажми 'Дальше'.</i>", parse_mode="HTML")
        return
    
    # Сохраняем file_id фотографии
    photo_id = message.photo[-1].file_id
    photos.append(photo_id)
    await state.update_data(photos=photos)
    
    await message.answer(
        f"👍 <b>Фото {len(photos)}/3</b> сохранено.\n<i>Продолжай или нажми 'Дальше'.</i>", 
        reply_markup=get_photos_done_keyboard(),
        parse_mode="HTML"
    )

async def photos_done(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Двигаемся дальше" после загрузки фотографий
    
    :param callback: Обратный вызов
    :param state: Состояние FSM
    """
    await callback.answer()
    
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        await callback.message.answer("⚠️ <b>Нужно хотя бы одно фото!</b>\n<i>Загрузи фото товара.</i>", parse_mode="HTML")
        return
    
    await callback.message.answer(
        "✏️ <b>Название товара</b>\n\n"
        "<i>Напиши краткое название (до 50 символов).</i>\n\n"
        "💡 <u>Например:</u> <code>Седло Brooks B17</code> или <code>Переключатель Shimano XT</code>",
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние ожидания заголовка
    await state.set_state(AdStates.waiting_for_title)

async def process_title(message: types.Message, state: FSMContext):
    """
    Обработчик заголовка объявления
    
    :param message: Сообщение
    :param state: Состояние FSM
    """
    if len(message.text) > 50:
        await message.answer("❌ <b>Слишком длинно!</b>\n<i>Сократи до 50 символов.</i>", reply_markup=get_error_keyboard(), parse_mode="HTML")
        return
    
    # Сохраняем заголовок
    await state.update_data(title=message.text)
    
    await message.answer(
        "📝 <b>Описание</b>\n\n"
        "<i>Расскажи о товаре: состояние, особенности, совместимость.</i>\n\n"
        "💭 <u>Совет:</u> Будь честным - это ценится больше приукрашивания.\n\n"
        "📏 <code>Максимум 500 символов</code>",
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние ожидания описания
    await state.set_state(AdStates.waiting_for_description)

async def process_description(message: types.Message, state: FSMContext):
    """
    Обработчик описания объявления
    
    :param message: Сообщение
    :param state: Состояние FSM
    """
    if len(message.text) > 500:
        await message.answer("❌ <b>Слишком много текста!</b>\n<i>Сократи до 500 символов.</i>", reply_markup=get_error_keyboard(), parse_mode="HTML")
        return
    
    # Сохраняем описание
    await state.update_data(description=message.text)
    
    await message.answer(
        "💰 <b>Цена</b>\n\n"
        "<i>Укажи цену в рублях (только число) или напиши</i> <code>Даром</code>",
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние ожидания цены
    await state.set_state(AdStates.waiting_for_price)

async def process_price(message: types.Message, state: FSMContext):
    """
    Обработчик цены объявления
    
    :param message: Сообщение
    :param state: Состояние FSM
    """
    price_text = message.text.strip()
    
    # Проверяем, что введено число
    try:
        formatted_price = format_price(price_text)
    except ValueError:
        await message.answer("❌ <b>Неверный формат цены!</b>\n<i>Введи число</i> (<code>5000</code>) <i>или</i> <code>Даром</code>", reply_markup=get_error_keyboard(), parse_mode="HTML")
        return
    
    # Сохраняем цену и данные пользователя
    user_mention = get_user_mention(message.from_user)
    user_display = get_user_display(message.from_user)
    
    # Добавляем отладочный лог
    logger = logging.getLogger(__name__)
    logger.info(f"Проверка username пользователя: ID={message.from_user.id}, username={message.from_user.username}")
    
    await state.update_data(
        price=formatted_price,
        user_id=message.from_user.id,
        user_mention=user_mention,
        user_display=user_display
    )
    
    # Получаем все собранные данные
    data = await state.get_data()
    
    # Создаем текст объявления
    preview_text = create_ad_text(data)
    
    # Проверяем наличие username у пользователя
    if not message.from_user.username:
        logger.warning(f"Пользователь без username: ID={message.from_user.id}")
        await message.answer(
            "⚠️ <b>У тебя нет @username!</b>\n\n"
            "<i>Без username покупателям будет сложно связаться с тобой.</i>\n\n"
            "🛠 <u>Решение:</u> создай <code>@username</code> в настройках Telegram или укажи альтернативный способ связи в описании.",
            parse_mode="HTML"
        )
    
    # Отправляем фотографии в одном сообщении с текстом
    photos = data['photos']
    if photos:
        # Создаем группу медиа
        media_group = create_media_group(photos, preview_text, "HTML")
        
        # Отправляем группу фотографий
        await message.answer_media_group(media=media_group)
    
    await message.answer(
        "👀 <b>Предварительный просмотр</b>\n\n"
        "<i>Проверь, что всё правильно.</i> Если да - <u>отправляй на модерацию!</u> 🚀",
        reply_markup=get_review_keyboard(),
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние просмотра
    await state.set_state(AdStates.review)

async def send_to_moderation(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик отправки на модерацию
    
    :param callback: Обратный вызов
    :param state: Состояние FSM
    """
    await callback.answer()
    
    # Получаем все данные объявления
    data = await state.get_data()
    
    # Проверяем наличие username у пользователя
    user_id = data.get("user_id")
    user = callback.from_user
    logger = logging.getLogger(__name__)
    logger.info(f"Отправка на модерацию: ID={user.id}, username={user.username}")
    
    if not user.username:
        logger.warning(f"Пользователь без username отправляет объявление на модерацию: ID={user.id}")
        await callback.message.answer(
            "⚠️ <b>Нет @username!</b>\n\n"
            "<i>Создай</i> <code>@username</code> <i>в настройках Telegram или укажи альтернативный способ связи в описании.</i>",
            parse_mode="HTML"
        )
    
    # Сохраняем ID сообщения и пользователя для использования после модерации
    post_data = {
        "user_id": data["user_id"],
        "category": data.get("category", "sell"),  # Добавляем категорию
        "photos": data["photos"],
        "title": data["title"],
        "description": data["description"],
        "price": data["price"],
        "user_mention": data["user_mention"],
        "user_display": data["user_display"]
    }
    
    # Сохраняем объявление в базу данных
    ad_id = db.save_moderation_ad(data['user_id'], post_data)
    
    # Формируем текст объявления для модерации
    mod_text = create_ad_text(data, is_moderation=True)
    
    # Отправляем фотографии в одном сообщении с текстом в чат модерации (если есть)
    photos = data.get('photos') or []
    if photos:
        media_group = create_media_group(photos, mod_text, "HTML")
        await bot.send_media_group(chat_id=MODERATION_CHAT_ID, media=media_group)

    # Всегда отправляем сообщение с кнопками модерации
    await bot.send_message(
        chat_id=MODERATION_CHAT_ID,
        text="🧠 <b>Новое объявление на модерации</b>",
        reply_markup=get_moderation_keyboard(ad_id),
        parse_mode="HTML"
    )
    
    # Сообщаем пользователю, что объявление отправлено на модерацию
    await callback.message.answer(
        "✅ <b>Отправлено на модерацию!</b>\n\n"
        "<i>Модераторы проверят твое объявление.</i> ⏰ Обычно это занимает до <code>24 часов</code>.\n\n"
        "Хочешь создать ещё одно объявление?",
        reply_markup=get_create_new_ad_keyboard(),
        parse_mode="HTML"
    )
    
    # Очищаем состояние пользователя
    await state.clear()

async def go_to_start(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик возврата в главное меню
    
    :param callback: Обратный вызов
    :param state: Состояние FSM
    """
    await callback.answer()
    
    # Очищаем состояние
    await state.clear()
    
    await callback.message.edit_text(
        "🎭 <b>Привет!</b>\n\n"
        "Добро пожаловать в <b>FGP_MIXEDBARAHOLKA</b>!\n\n"
        "<i>Здесь можно продать вещи и анонсировать события.</i>",
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    ) 