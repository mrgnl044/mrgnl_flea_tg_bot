import sqlite3
import json
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для работы с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Инициализация базы данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица для хранения состояния пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_states (
                    user_id INTEGER PRIMARY KEY,
                    state TEXT,
                    data TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица для хранения объявлений на модерации
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS moderation_ads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT,
                    photos TEXT,
                    title TEXT,
                    description TEXT,
                    price TEXT,
                    user_mention TEXT,
                    user_display TEXT,
                    moderation_message_id INTEGER,
                    moderation_chat_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    moderated_at TIMESTAMP,
                    moderator_id INTEGER
                )
            """)
            
            # Таблица для опубликованных объявлений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS published_ads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT,
                    photos TEXT,
                    title TEXT,
                    description TEXT,
                    price TEXT,
                    user_mention TEXT,
                    user_display TEXT,
                    channel_message_id INTEGER,
                    channel_chat_id INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sold_at TIMESTAMP,
                    sold_by_user_id INTEGER
                )
            """)
            
            conn.commit()
            logger.info("База данных инициализирована")
    
    def save_user_state(self, user_id: int, state: str, data: Dict[str, Any]):
        """Сохраняет состояние пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_states (user_id, state, data, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, state, json.dumps(data, ensure_ascii=False)))
            conn.commit()
            logger.debug(f"Состояние пользователя {user_id} сохранено: {state}")
    
    def get_user_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает состояние пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT state, data FROM user_states WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'state': row['state'],
                    'data': json.loads(row['data']) if row['data'] else {}
                }
            return None
    
    def clear_user_state(self, user_id: int):
        """Очищает состояние пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_states WHERE user_id = ?", (user_id,))
            conn.commit()
            logger.debug(f"Состояние пользователя {user_id} очищено")
    
    def save_moderation_ad(self, user_id: int, ad_data: Dict[str, Any]) -> int:
        """Сохраняет объявление на модерации"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO moderation_ads (
                    user_id, category, photos, title, description, price,
                    user_mention, user_display
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                ad_data.get('category'),
                json.dumps(ad_data.get('photos', []), ensure_ascii=False),
                ad_data.get('title'),
                ad_data.get('description'),
                ad_data.get('price'),
                ad_data.get('user_mention'),
                ad_data.get('user_display')
            ))
            conn.commit()
            ad_id = cursor.lastrowid
            logger.info(f"Объявление {ad_id} пользователя {user_id} сохранено на модерации")
            return ad_id
    
    def get_moderation_ad(self, ad_id: int) -> Optional[Dict[str, Any]]:
        """Получает объявление на модерации"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM moderation_ads WHERE id = ?
            """, (ad_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'category': row['category'],
                    'photos': json.loads(row['photos']) if row['photos'] else [],
                    'title': row['title'],
                    'description': row['description'],
                    'price': row['price'],
                    'user_mention': row['user_mention'],
                    'user_display': row['user_display'],
                    'moderation_message_id': row['moderation_message_id'],
                    'moderation_chat_id': row['moderation_chat_id'],
                    'status': row['status'],
                    'created_at': row['created_at']
                }
            return None
    
    def update_moderation_status(self, ad_id: int, status: str, moderator_id: int, 
                               moderation_message_id: int = None, moderation_chat_id: int = None):
        """Обновляет статус модерации"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE moderation_ads 
                SET status = ?, moderator_id = ?, moderated_at = CURRENT_TIMESTAMP,
                    moderation_message_id = ?, moderation_chat_id = ?
                WHERE id = ?
            """, (status, moderator_id, moderation_message_id, moderation_chat_id, ad_id))
            conn.commit()
            logger.info(f"Статус объявления {ad_id} обновлен на {status}")
    
    def save_published_ad(self, user_id: int, ad_data: Dict[str, Any], 
                         channel_message_id: int, channel_chat_id: int) -> int:
        """Сохраняет опубликованное объявление"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO published_ads (
                    user_id, category, photos, title, description, price,
                    user_mention, user_display, channel_message_id, channel_chat_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                ad_data.get('category'),
                json.dumps(ad_data.get('photos', []), ensure_ascii=False),
                ad_data.get('title'),
                ad_data.get('description'),
                ad_data.get('price'),
                ad_data.get('user_mention'),
                ad_data.get('user_display'),
                channel_message_id,
                channel_chat_id
            ))
            conn.commit()
            ad_id = cursor.lastrowid
            logger.info(f"Объявление {ad_id} пользователя {user_id} опубликовано")
            return ad_id
    
    def get_published_ad(self, ad_id: int) -> Optional[Dict[str, Any]]:
        """Получает опубликованное объявление"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM published_ads WHERE id = ?
            """, (ad_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'category': row['category'],
                    'photos': json.loads(row['photos']) if row['photos'] else [],
                    'title': row['title'],
                    'description': row['description'],
                    'price': row['price'],
                    'user_mention': row['user_mention'],
                    'user_display': row['user_display'],
                    'channel_message_id': row['channel_message_id'],
                    'channel_chat_id': row['channel_chat_id'],
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'sold_at': row['sold_at'],
                    'sold_by_user_id': row['sold_by_user_id']
                }
            return None
    
    def mark_ad_as_sold(self, ad_id: int, sold_by_user_id: int):
        """Отмечает объявление как проданное"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE published_ads 
                SET status = 'sold', sold_at = CURRENT_TIMESTAMP, sold_by_user_id = ?
                WHERE id = ?
            """, (sold_by_user_id, ad_id))
            conn.commit()
            logger.info(f"Объявление {ad_id} отмечено как проданное пользователем {sold_by_user_id}")
    
    def get_user_ads(self, user_id: int) -> List[Dict[str, Any]]:
        """Получает все объявления пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM published_ads WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            
            return [{
                'id': row['id'],
                'category': row['category'],
                'title': row['title'],
                'price': row['price'],
                'status': row['status'],
                'created_at': row['created_at'],
                'channel_message_id': row['channel_message_id'],
                'channel_chat_id': row['channel_chat_id']
            } for row in rows]

# Глобальный экземпляр базы данных
db = Database()
