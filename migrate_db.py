#!/usr/bin/env python3
"""
Исправленный скрипт миграции базы данных
Безопасное удаление таблицы с внешними ключами
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
import shutil

def migrate_database():
    """Выполнить миграцию базы данных"""
    
    # Путь к базе данных
    base_dir = Path(__file__).parent.parent
    # db_path = base_dir / "app" / "assets" / "database" / "plant_protection.db"
    db_path = base_dir / "plant_protection_app" / "app" / "assets" / "database" / "plant_protection.db"

    
    # Создаем резервную копию
    backup_path = db_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    
    print(f"🔧 Начинаем миграцию базы данных...")
    print(f"📁 База данных: {db_path}")
    
    if not db_path.exists():
        print(f"❌ Файл базы данных не найден: {db_path}")
        return False
    
    try:
        # Создаем резервную копию
        shutil.copy2(db_path, backup_path)
        print(f"✅ Создана резервная копия: {backup_path}")
        
        # Подключаемся к БД
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # ВАЖНО: Отключаем внешние ключи на время миграции
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        print("1. Проверяем текущую структуру...")
        
        # Проверяем существующие таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Найдены таблицы: {', '.join(tables)}")
        
        # 1. Сохраняем данные из зависимых таблиц
        print("2. Сохраняем данные из зависимых таблиц...")
        
        # Сохраняем данные из pesticide_active_substances
        cursor.execute("SELECT * FROM pesticide_active_substances")
        pas_data = cursor.fetchall()
        print(f"   Сохранено {len(pas_data)} записей из pesticide_active_substances")
        
        # Сохраняем данные из pesticide_cultures
        cursor.execute("SELECT * FROM pesticide_cultures")
        pc_data = cursor.fetchall()
        print(f"   Сохранено {len(pc_data)} записей из pesticide_cultures")
        
        # Сохраняем данные из pesticide_diseases
        cursor.execute("SELECT * FROM pesticide_diseases")
        pd_data = cursor.fetchall()
        print(f"   Сохранено {len(pd_data)} записей из pesticide_diseases")
        
        # Сохраняем данные из order_items
        cursor.execute("SELECT * FROM order_items")
        oi_data = cursor.fetchall()
        print(f"   Сохранено {len(oi_data)} записей из order_items")
        
        # 2. Удаляем зависимые таблицы
        print("3. Удаляем зависимые таблицы...")
        
        # Временное отключение проверки внешних ключей
        cursor.execute("PRAGMA defer_foreign_keys = ON")
        
        # Удаляем таблицы в правильном порядке (от зависимых к родительским)
        cursor.execute("DROP TABLE IF EXISTS order_items")
        cursor.execute("DROP TABLE IF EXISTS pesticide_active_substances")
        cursor.execute("DROP TABLE IF EXISTS pesticide_cultures")
        cursor.execute("DROP TABLE IF EXISTS pesticide_diseases")
        print("   ✅ Зависимые таблицы удалены")
        
        # 3. Обновляем таблицу pesticides
        print("4. Обновляем таблицу pesticides...")
        
        # Получаем структуру старой таблицы
        cursor.execute("PRAGMA table_info(pesticides)")
        old_columns = cursor.fetchall()
        print(f"   Старые колонки: {[col[1] for col in old_columns]}")
        
        # Сохраняем данные из pesticides
        cursor.execute("SELECT * FROM pesticides")
        pesticides_data = cursor.fetchall()
        print(f"   Сохранено {len(pesticides_data)} записей из pesticides")
        
        # Удаляем старую таблицу pesticides
        cursor.execute("DROP TABLE IF EXISTS pesticides")
        
        # Создаем новую таблицу pesticides (без unit_of_measure)
        cursor.execute('''
            CREATE TABLE pesticides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                application_rate TEXT,
                packaging TEXT,
                price DECIMAL(10, 2),
                manufacturer TEXT,
                pesticide_type_id INTEGER REFERENCES pesticide_types(id)
            )
        ''')
        
        # Восстанавливаем данные в новую таблицу
        for row in pesticides_data:
            cursor.execute('''
                INSERT INTO pesticides (id, name, description, application_rate, packaging, price, manufacturer, pesticide_type_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['id'],
                row['name'],
                row['description'],
                row['application_rate'],
                row['packaging'],
                row['price'],
                row['manufacturer'],
                row['pesticide_type_id']
            ))
        
        print("   ✅ Таблица pesticides обновлена (удален unit_of_measure)")
        
        # 4. Воссоздаем зависимые таблицы с новой структурой
        print("5. Воссоздаем зависимые таблицы...")
        
        # Создаем pesticide_active_substances с concentration
        cursor.execute('''
            CREATE TABLE pesticide_active_substances (
                pesticide_id INTEGER REFERENCES pesticides(id),
                substance_id INTEGER REFERENCES active_substances(id),
                concentration TEXT,
                PRIMARY KEY (pesticide_id, substance_id)
            )
        ''')
        
        # Восстанавливаем данные с концентрацией по умолчанию
        for row in pas_data:
            cursor.execute('''
                INSERT INTO pesticide_active_substances (pesticide_id, substance_id, concentration)
                VALUES (?, ?, ?)
            ''', (row['pesticide_id'], row['substance_id'], '500 г/л'))
        
        print(f"   ✅ Восстановлено {len(pas_data)} записей в pesticide_active_substances")
        
        # Воссоздаем pesticide_cultures
        cursor.execute('''
            CREATE TABLE pesticide_cultures (
                pesticide_id INTEGER REFERENCES pesticides(id),
                culture_id INTEGER REFERENCES cultures(id),
                PRIMARY KEY (pesticide_id, culture_id)
            )
        ''')
        
        for row in pc_data:
            cursor.execute('''
                INSERT INTO pesticide_cultures (pesticide_id, culture_id)
                VALUES (?, ?)
            ''', (row['pesticide_id'], row['culture_id']))
        
        print(f"   ✅ Восстановлено {len(pc_data)} записей в pesticide_cultures")
        
        # Воссоздаем pesticide_diseases
        cursor.execute('''
            CREATE TABLE pesticide_diseases (
                pesticide_id INTEGER REFERENCES pesticides(id),
                disease_id INTEGER REFERENCES diseases(id),
                PRIMARY KEY (pesticide_id, disease_id)
            )
        ''')
        
        for row in pd_data:
            cursor.execute('''
                INSERT INTO pesticide_diseases (pesticide_id, disease_id)
                VALUES (?, ?)
            ''', (row['pesticide_id'], row['disease_id']))
        
        print(f"   ✅ Восстановлено {len(pd_data)} записей в pesticide_diseases")
        
        # Воссоздаем order_items
        cursor.execute('''
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER REFERENCES orders(id),
                pesticide_id INTEGER REFERENCES pesticides(id),
                culture_id INTEGER REFERENCES cultures(id),
                quantity DECIMAL(10, 3),
                packaging TEXT,
                unit_price DECIMAL(10, 2),
                discount DECIMAL(5, 2) DEFAULT 0,
                discounted_price DECIMAL(10, 2),
                item_total DECIMAL(12, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        for row in oi_data:
            cursor.execute('''
                INSERT INTO order_items (id, order_id, pesticide_id, culture_id, quantity, packaging, unit_price, discount, discounted_price, item_total, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['id'],
                row['order_id'],
                row['pesticide_id'],
                row['culture_id'],
                row['quantity'],
                row['packaging'],
                row['unit_price'],
                row['discount'],
                row['discounted_price'],
                row['item_total'],
                row['created_at']
            ))
        
        print(f"   ✅ Восстановлено {len(oi_data)} записей в order_items")
        
        # 5. Создаем индексы
        print("6. Создаем индексы...")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pas_pesticide_id 
            ON pesticide_active_substances(pesticide_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pas_substance_id 
            ON pesticide_active_substances(substance_id)
        ''')
        
        print("   ✅ Индексы созданы")
        
        # 6. Включаем обратно внешние ключи
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 7. Проверяем целостность
        print("7. Проверяем целостность БД...")
        
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        
        if fk_errors:
            print(f"   ❌ Найдены ошибки внешних ключей: {fk_errors}")
            raise Exception("Ошибки внешних ключей после миграции")
        else:
            print("   ✅ Целостность БД проверена")
        
        # Сохраняем изменения
        conn.commit()
        
        # 8. Проверяем структуру
        print("\n8. Проверяем новую структуру...")
        print("-" * 50)
        
        cursor.execute("PRAGMA table_info(pesticides)")
        pesticides_columns = [row[1] for row in cursor.fetchall()]
        print(f"Таблица pesticides колонки: {pesticides_columns}")
        
        cursor.execute("PRAGMA table_info(pesticide_active_substances)")
        pas_columns = [row[1] for row in cursor.fetchall()]
        print(f"Таблица pesticide_active_substances колонки: {pas_columns}")
        
        print("-" * 50)
        print("Пример данных с концентрациями:")
        
        cursor.execute('''
            SELECT 
                p.name as Препарат,
                a.substance_name as ДВ,
                pas.concentration as Концентрация
            FROM pesticides p
            JOIN pesticide_active_substances pas ON p.id = pas.pesticide_id
            JOIN active_substances a ON pas.substance_id = a.id
            LIMIT 5
        ''')
        
        for row in cursor.fetchall():
            print(f"  {row['Препарат']}: {row['ДВ']} ({row['Концентрация']})")
        
        print("\n✅ Миграция успешно завершена!")
        print(f"📊 Резервная копия сохранена в: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n🔄 Восстанавливаем из резервной копии...")
        
        # Пытаемся восстановить из backup
        try:
            if backup_path.exists():
                # Закрываем соединение если открыто
                if 'conn' in locals():
                    conn.close()
                
                # Восстанавливаем файл
                shutil.copy2(backup_path, db_path)
                print(f"✅ Восстановлено из резервной копии")
        except Exception as restore_error:
            print(f"❌ Ошибка восстановления: {restore_error}")
        
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    print("=" * 50)
    print("МИГРАЦИЯ БАЗЫ ДАННЫХ Plant Protection App")
    print("Версия 2.0 - Безопасная миграция с внешними ключами")
    print("=" * 50)
    print("Изменения:")
    print("1. Удаляет unit_of_measure из таблицы pesticides")
    print("2. Добавляет concentration в pesticide_active_substances")
    print("=" * 50)
    
    response = input("\nПродолжить миграцию? (y/n): ").strip().lower()
    
    if response == 'y':
        success = migrate_database()
        if success:
            print("\n" + "=" * 50)
            print("🎉 Миграция завершена успешно!")
            print("=" * 50)
            print("Структура БД обновлена:")
            print("✓ pesticides: удален unit_of_measure")
            print("✓ pesticide_active_substances: добавлено concentration")
            print("\nТеперь можно обновлять интерфейс приложения.")
        else:
            print("\n❌ Миграция не удалась. Проверьте ошибки выше.")
    else:
        print("Миграция отменена.")

if __name__ == "__main__":
    main()