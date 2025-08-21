"""
Модуль обработчиков для телеграм-бота объявлений Fixed Gear Perm.
"""

from . import start, create_ad, moderation, user_actions

__all__ = ["start", "create_ad", "moderation", "user_actions"]

def register_all_handlers(dp):
    """
    Регистрирует все обработчики
    
    :param dp: Диспетчер
    """
    # Сначала регистрируем глобальные обработчики
    from .create_ad import go_to_start
    dp.callback_query.register(go_to_start, lambda c: c.data == "start_command")
    
    handlers = [
        start,
        create_ad,
        moderation,
        user_actions
    ]
    
    for handler in handlers:
        handler.register_handlers(dp) 