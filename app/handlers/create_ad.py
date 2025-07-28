"""
Обработчики создания объявления для телеграм-бота объявлений Fixed Gear Perm.
"""

from aiogram import types
from aiogram.fsm.context import FSMContext
import logging

from ..bot import bot, dp
from ..states import AdStates
from ..keyboards import get_photos_done_keyboard, get_review_keyboard, get_moderation_keyboard
from ..utils import (
    format_price, get_user_mention, get_user_display, 
    create_ad_text, create_media_group
)
from ..config import MODERATION_CHAT_ID

def register_handlers(dp):
    """
    Регистрирует обработчики создания объявления
    
    :param dp: Диспетчер
    """
    # Начало создания объявления
    dp.callback_query.register(create_ad, lambda c: c.data == "create_ad")
    
    # Обработка фотографий
    dp.message.register(process_photo, AdStates.waiting_for_photos, lambda message: message.photo)
    dp.callback_query.register(photos_done, AdStates.waiting_for_photos, lambda c: c.data == "photos_done")
    
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
    
    # Создаем пустой список для фотографий
    await state.update_data(photos=[])
    
    await callback.message.answer(
        "📸 <b>Шаг 1/4: Фотосессия вашего товара</b>\n\n"
        "Пожалуйста, сделайте до 3-х снимков вашего лота – будь то велосипед, запчасть или аксессуар. "
        "Помните, что хорошие фотографии увеличивают шансы на продажу! Покажите товар с выгодных ракурсов, чтобы были видны все особенности и состояние.\n\n"
        "После загрузки нажмите кнопку 'Двигаемся дальше'.\n\n"
        "Совет: Если вы продаёте мелкие детали, расположите их на контрастном фоне – так они будут лучше видны.",
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние ожидания фотографий
    await state.set_state(AdStates.waiting_for_photos)
    
    # Отправляем сообщение с кнопкой "Продолжить"
    await callback.message.answer(
        "После завершения фотографирования:", 
        reply_markup=get_photos_done_keyboard()
    )

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
        await message.answer("🧐 Ваш энтузиазм заслуживает признания, но даже для самой редкой детали достаточно трёх фотографий. Пожалуйста, нажмите 'Двигаемся дальше'.")
        return
    
    # Сохраняем file_id фотографии
    photo_id = message.photo[-1].file_id
    photos.append(photo_id)
    await state.update_data(photos=photos)
    
    await message.answer(
        f"👌 Отличный кадр! Фото {len(photos)}/3 сохранено. Продолжайте или нажмите 'Двигаемся дальше', если завершили съёмку.", 
        reply_markup=get_photos_done_keyboard()
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
        await callback.message.answer("🧩 Необходимо загрузить хотя бы одну фотографию вашего товара! Даже если это гайка размером с ноготь, покупатели хотят видеть, что именно они приобретают.")
        return
    
    await callback.message.answer(
        "✒️ <b>Шаг 2/4: Название вашего лота</b>\n\n"
        "Придумайте краткое, но информативное название для вашего товара. Хорошее название должно содержать ключевую информацию: что это, для какого велосипеда подходит, возможно, бренд или особенность.\n\n"
        "Например: «Седло Brooks B17 Imperial, чёрное» или «Переключатель Shimano Deore XT, новый» (не более 50 символов).",
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
        await message.answer("📏 Уважаемый автор, ваша фантазия прекрасна, но название должно быть компактным – не более 50 символов. Сократите, пожалуйста, сохранив суть.")
        return
    
    # Сохраняем заголовок
    await state.update_data(title=message.text)
    
    await message.answer(
        "📝 <b>Шаг 3/4: Описание товара</b>\n\n"
        "Теперь расскажите подробнее о вашем лоте. Для велосипеда укажите размер рамы, год выпуска, пробег, состояние. Для компонентов – совместимость, состояние (новое/б/у), особенности.\n\n"
        "Не стесняйтесь упомянуть как достоинства, так и недостатки товара – честность ценится покупателями больше, чем приукрашивание.\n\n"
        "Пожалуйста, уложитесь в 500 символов – краткость и информативность в приоритете.",
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
        await message.answer("📚 Ваше описание впечатляюще детально, но нам нужен формат скорее краткой аннотации, чем полного технического паспорта. Пожалуйста, сократите до 500 символов, выделив самое важное.")
        return
    
    # Сохраняем описание
    await state.update_data(description=message.text)
    
    await message.answer(
        "💰 <b>Шаг 4/4: Ценообразование</b>\n\n"
        "Какую цену вы хотите установить за этот товар? Если это редкий или коллекционный предмет, не стесняйтесь указать соответствующую цену. Если же вы просто хотите избавиться от ненужного хлама, цена может быть более демократичной.\n\n"
        "Укажите стоимость в рублях (только число) или напишите «Даром», если готовы отдать бесплатно.",
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
        await message.answer("💹 К сожалению, наша система не распознала указанную цену. Пожалуйста, введите только число (например: 5000) или слово «Даром» – без дополнительных символов или пояснений.")
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
        # Отправляем предупреждение ПЕРЕД группой фотографий для большей заметности
        await message.answer(
            "🧐 <b>ВНИМАНИЕ: У ВАС НЕТ @USERNAME!</b> 🧐\n\n"
            "Без username в Telegram потенциальным покупателям будет сложно связаться с вами напрямую.\n"
            "Настоятельно рекомендуем либо создать @username в настройках Telegram,\n"
            "либо указать в описании товара альтернативный способ связи (телефон, мессенджер или соцсеть).",
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
        "🖼️ <b>Предварительный просмотр вашего объявления</b>\n\n"
        "Взгляните на финальный вид вашего объявления! Убедитесь, что все данные указаны корректно, фотографии хорошо отображают товар, а описание содержит всю важную информацию.\n\n"
        "Если всё в порядке, отправляйте на модерацию. Если нужно что-то изменить – начните процесс заново.",
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
            "📢 <b>ПОСЛЕДНЕЕ НАПОМИНАНИЕ О КОНТАКТАХ!</b> 📢\n\n"
            "В вашем профиле Telegram до сих пор нет @username!\n"
            "Это значительно усложнит процесс связи с потенциальными покупателями.\n\n"
            "Рекомендуем сейчас же создать @username в настройках Telegram\n"
            "или обязательно указать в описании товара альтернативный способ связи.",
            parse_mode="HTML"
        )
    
    # Сохраняем ID сообщения и пользователя для использования после модерации
    post_data = {
        "user_id": data["user_id"],
        "photos": data["photos"],
        "title": data["title"],
        "description": data["description"],
        "price": data["price"],
        "user_mention": data["user_mention"],
        "user_display": data["user_display"]
    }
    
    # Формируем текст объявления для модерации
    mod_text = create_ad_text(data, is_moderation=True)
    
    # Отправляем фотографии в одном сообщении с текстом в чат модерации
    photos = data['photos']
    if photos:
        # Создаем группу медиа
        media_group = create_media_group(photos, mod_text, "HTML")
        
        # Отправляем группу фотографий в чат модерации
        sent_messages = await bot.send_media_group(chat_id=MODERATION_CHAT_ID, media=media_group)
        
        # Отправляем сообщение с кнопками отдельно, ссылаясь на первое фото
        await bot.send_message(
            chat_id=MODERATION_CHAT_ID,
            text="🧠 <b>Требуется модерация нового объявления</b>\n\nПожалуйста, проверьте соответствие объявления правилам сообщества и примите решение о публикации.",
            reply_markup=get_moderation_keyboard(data['user_id']),
            parse_mode="HTML"
        )
    
    # Сохраняем данные объявления в хранилище с ключом, содержащим ID пользователя
    await dp.storage.set_data(key=f"ad_{data['user_id']}", data=post_data)
    
    # Сообщаем пользователю, что объявление отправлено на модерацию
    await callback.message.answer(
        "📋 <b>Ваше объявление отправлено на модерацию!</b>\n\n"
        "Наши модераторы проверят ваше объявление на соответствие правилам сообщества. "
        "После проверки вы получите уведомление о публикации или отклонении. "
        "Обычно процесс занимает не более 24 часов. Спасибо за терпение!",
        parse_mode="HTML"
    )
    
    # Очищаем состояние пользователя
    await state.clear() 