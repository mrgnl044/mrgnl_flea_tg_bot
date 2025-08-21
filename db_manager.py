#!/usr/bin/env python3
"""
Скрипт для управления базой данных бота
"""

import sqlite3
import json
from datetime import datetime

def print_table_data(table_name):
    """Выводит данные из таблицы"""
    print(f"\n=== {table_name.upper()} ===")
    conn = sqlite3.connect('bot_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print("Таблица пуста")
        return
    
    for row in rows:
        # Определяем основной ключ в зависимости от таблицы
        if table_name == 'user_states':
            primary_key = 'user_id'
        else:
            primary_key = 'id'
        
        print(f"{primary_key.upper()}: {row[primary_key]}")
        for key in row.keys():
            if key != primary_key:
                value = row[key]
                if value is None:
                    print(f"  {key}: NULL")
                elif isinstance(value, str) and value.startswith('['):
                    try:
                        parsed = json.loads(value)
                        print(f"  {key}: {len(parsed)} элементов")
                    except:
                        print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")
        print("-" * 40)
    
    conn.close()

def clear_table(table_name):
    """Очищает таблицу"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name}")
    conn.commit()
    conn.close()
    print(f"Таблица {table_name} очищена")

def show_stats():
    """Показывает статистику базы данных"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    # Подсчет записей в каждой таблице
    tables = ['user_states', 'moderation_ads', 'published_ads']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} записей")
    
    # Статистика по статусам модерации
    cursor.execute("SELECT status, COUNT(*) FROM moderation_ads GROUP BY status")
    status_stats = cursor.fetchall()
    print("\nСтатистика модерации:")
    for status, count in status_stats:
        print(f"  {status}: {count}")
    
    # Статистика по статусам опубликованных объявлений
    cursor.execute("SELECT status, COUNT(*) FROM published_ads GROUP BY status")
    pub_stats = cursor.fetchall()
    print("\nСтатистика опубликованных объявлений:")
    for status, count in pub_stats:
        print(f"  {status}: {count}")
    
    conn.close()

def main():
    """Главная функция"""
    while True:
        print("\n=== УПРАВЛЕНИЕ БАЗОЙ ДАННЫХ ===")
        print("1. Показать статистику")
        print("2. Показать user_states")
        print("3. Показать moderation_ads")
        print("4. Показать published_ads")
        print("5. Очистить user_states")
        print("6. Очистить moderation_ads")
        print("7. Очистить published_ads")
        print("8. Очистить все таблицы")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == '1':
            show_stats()
        elif choice == '2':
            print_table_data('user_states')
        elif choice == '3':
            print_table_data('moderation_ads')
        elif choice == '4':
            print_table_data('published_ads')
        elif choice == '5':
            if input("Уверены? (y/N): ").lower() == 'y':
                clear_table('user_states')
        elif choice == '6':
            if input("Уверены? (y/N): ").lower() == 'y':
                clear_table('moderation_ads')
        elif choice == '7':
            if input("Уверены? (y/N): ").lower() == 'y':
                clear_table('published_ads')
        elif choice == '8':
            if input("Уверены? Это удалит ВСЕ данные! (y/N): ").lower() == 'y':
                clear_table('user_states')
                clear_table('moderation_ads')
                clear_table('published_ads')
        elif choice == '0':
            break
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main()
