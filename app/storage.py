from typing import Any, Dict, Optional
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from .database import db
import json

class DatabaseStorage(BaseStorage):
    """Кастомное хранилище FSM на основе базы данных"""
    
    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        """Устанавливает состояние"""
        user_id = key.user_id
        current_data = db.get_user_state(user_id) or {'data': {}}
        
        if state is None:
            # Очищаем состояние
            db.clear_user_state(user_id)
        else:
            # Обновляем состояние
            current_data['state'] = state.state if hasattr(state, 'state') else str(state)
            db.save_user_state(user_id, current_data['state'], current_data['data'])
    
    async def get_state(self, key: StorageKey) -> Optional[str]:
        """Получает состояние"""
        user_id = key.user_id
        state_data = db.get_user_state(user_id)
        return state_data['state'] if state_data else None
    
    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        """Устанавливает данные"""
        user_id = key.user_id
        current_state = db.get_user_state(user_id)
        state = current_state['state'] if current_state else None
        
        db.save_user_state(user_id, state, data)
    
    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        """Получает данные"""
        user_id = key.user_id
        state_data = db.get_user_state(user_id)
        return state_data['data'] if state_data else {}
    
    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновляет данные"""
        user_id = key.user_id
        current_state = db.get_user_state(user_id)
        state = current_state['state'] if current_state else None
        current_data = current_state['data'] if current_state else {}
        
        # Обновляем данные
        current_data.update(data)
        
        db.save_user_state(user_id, state, current_data)
        return current_data
    
    async def clear(self, key: StorageKey) -> None:
        """Очищает состояние и данные"""
        user_id = key.user_id
        db.clear_user_state(user_id)

    async def close(self) -> None:
        """Закрывает хранилище (совместимость с интерфейсом BaseStorage)"""
        return None
