# Умный экспорт: app\ui\screens\catalog_screen.py
**Дата:** 2025-12-15 16:54:05
**Целевой файл:** `app\ui\screens\catalog_screen.py`
**Проект:** plant_protection_app

## Обзор зависимостей

```
Целевой файл: app\ui\screens\catalog_screen.py
Зависимости:
  ├── app\core\database.py
  ├── app\core\database_backup.py
  ├── app\ml\model_loader.py
  ├── app\ui\__init__.py
  ├── app\ui\screens\__init__.py
  ├── app\ui\screens\substance_editor.py
  ├── app\ui\widgets\__init__.py
  ├── app\ui\widgets\substance_item.py
  ├── export_project_v1.py
  ├── main.py
  ├── main_db_test.py
  ├── migrate_db.py
  ├── pyproject.toml
  ├── smart_export_full.py
  ├── smart_export_short.py
```

## Структура экспорта

```
```

## Структура базы данных

### База данных: `app\assets\database\plant_protection.backup_20251206_135838.db`

**Таблицы:**

#### Таблица: `active_substances`

| Колонка | Тип | Nullable | Default | PK |
|---------|-----|----------|---------|----|
| `id` | `INTEGER` | Да | `NULL` | Да |
| `substance_name` | `TEXT` | Нет | `NULL` | Нет |

**Индексы:**

Ошибка при чтении базы данных: too many values to unpack (expected 3)

### База данных: `app\assets\database\plant_protection.db`

**Таблицы:**

#### Таблица: `active_substances`

| Колонка | Тип | Nullable | Default | PK |
|---------|-----|----------|---------|----|
| `id` | `INTEGER` | Да | `NULL` | Да |
| `substance_name` | `TEXT` | Нет | `NULL` | Нет |

**Индексы:**

Ошибка при чтении базы данных: too many values to unpack (expected 3)

## Содержимое файлов

### app\core\database.py
**Размер:** 19573 байт  
```python
import sqlite3
from pathlib import Path
from app.core.config import AppConfig

class DatabaseManager:
    """Менеджер базы данных SQLite"""
    
    def __init__(self):
        # Прямой путь к БД без использования Config
        base_dir = Path(__file__).parent.parent.parent
        self.database_path = base_dir / "app" / "assets" / "database" / "plant_protection.db"
        self.connection = None
        
        # Создаем директорию если не существует
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
    
    def initialize(self):
        """Инициализация базы данных"""
        try:
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row
            self._create_tables()
            self._insert_sample_data()
            print("✅ База данных инициализирована успешно")
            print(f"📁 Путь к БД: {self.database_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            return False
    
    def _create_tables(self):
        """Создание таблиц базы данных согласно схеме"""
        cursor = self.connection.cursor()
        
        # 1. Таблица типов пестицидов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # 2. Таблица культур
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cultures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                culture_name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # 3. Таблица действующих веществ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_substances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                substance_name TEXT NOT NULL UNIQUE
            )
        ''')
        

        # 4. Таблица классов заболеваний для нейросети (упрощенная)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_classes (
                class_index INTEGER PRIMARY KEY,  -- Индекс из нейросети как PRIMARY KEY
                class_name TEXT NOT NULL UNIQUE   -- Название заболевания
            )
        ''')

        # 5. Таблица болезней растений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_name TEXT NOT NULL UNIQUE,
                symptoms TEXT,
                prevention_methods TEXT,
                culture_id INTEGER REFERENCES cultures(id),
                disease_class_index INTEGER REFERENCES disease_classes(class_index)  -- Привязка к class_index
            )
        ''')
        
        # 6. Таблица пестицидов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                application_rate TEXT,
                packaging TEXT,
                price DECIMAL(10, 2),
                manufacturer TEXT,
                unit_of_measure TEXT,
                # image_url TEXT,
                pesticide_type_id INTEGER REFERENCES pesticide_types(id)
            )
        ''')
        
        # 7. Связующие таблицы
        
        # Пестициды - Действующие вещества
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_active_substances (
                pesticide_id INTEGER REFERENCES pesticides(id),
                substance_id INTEGER REFERENCES active_substances(id),
                concentration TEXT,
                PRIMARY KEY (pesticide_id, substance_id)
            )
        ''')
        
        # Пестициды - Культуры
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_cultures (
                pesticide_id INTEGER REFERENCES pesticides(id),
                culture_id INTEGER REFERENCES cultures(id),
                PRIMARY KEY (pesticide_id, culture_id)
            )
        ''')
        
        # Пестициды - Болезни
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_diseases (
                pesticide_id INTEGER REFERENCES pesticides(id),
                disease_id INTEGER REFERENCES diseases(id),
                PRIMARY KEY (pesticide_id, disease_id)
            )
        ''')
        
        # 8. Таблица клиентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                total_orchard_area DECIMAL(10, 2),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 9. Таблица культур клиента
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_cultures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER REFERENCES clients(id),
                culture_id INTEGER REFERENCES cultures(id),
                area DECIMAL(10, 2),
                UNIQUE(client_id, culture_id)
            )
        ''')
        
        # 10. Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE,
                client_id INTEGER REFERENCES clients(id),
                order_date DATE NOT NULL,
                shipment_date DATE,
                payment_date DATE,
                total_amount DECIMAL(12, 2),
                status TEXT DEFAULT 'черновик',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 11. Таблица позиций заказа
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
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
        
        self.connection.commit()
        print("✅ Таблицы базы данных созданы")
        # Загружаем классы заболеваний из файла
        self._load_disease_classes_from_file()
    
    def _insert_sample_data(self):
     """Вставка тестовых данных - ОСНОВНАЯ ВЕРСИЯ (пустая)"""
    # В основной версии не заполняем тестовыми данными
    # Данные будут добавляться через админку или импорт
    pass

    # Методы для работы с данными
    
    def get_disease_class_by_index(self, class_index):
        """Получение класса заболевания по индексу нейросети"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM disease_classes 
            WHERE class_index = ?
        ''', (class_index,))
        return cursor.fetchone()

    def get_all_disease_classes(self):
        """Получение всех классов заболеваний"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM disease_classes 
            ORDER BY class_index
        ''')
        return cursor.fetchall()

    def update_disease_classes_from_file(self):
        """Обновление классов заболеваний из файла"""
        print("🔄 Обновление классов заболеваний...")
        self._load_disease_classes_from_file()
        return True
   
    
    def get_recommendations_for_disease_class(self, class_index):
        """Получение рекомендаций для класса заболевания"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT p.* FROM pesticides p
            JOIN pesticide_diseases pd ON p.id = pd.pesticide_id
            JOIN diseases d ON pd.disease_id = d.id
            WHERE d.disease_class_id = ?
            LIMIT 10
        ''', (class_index,))
        return cursor.fetchall()
    
    def get_all_active_substances(self):
        """Получение всех доступных действующих веществ"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT id, substance_name 
            FROM active_substances 
            ORDER BY substance_name
        ''')
        return [{'id': row['id'], 'name': row['substance_name']} for row in cursor.fetchall()]

    def save_pesticide_substances(self, pesticide_id, substances_list):
        """Сохранение списка действующих веществ для пестицида"""
        cursor = self.connection.cursor()
        
        # Удаляем старые связи
        cursor.execute('DELETE FROM pesticide_active_substances WHERE pesticide_id = ?', (pesticide_id,))
        
        # Добавляем новые
        for substance in substances_list:
            cursor.execute('''
                INSERT INTO pesticide_active_substances (pesticide_id, substance_id, concentration)
                VALUES (?, ?, ?)
            ''', (pesticide_id, substance['id'], substance['concentration']))
        
        self.connection.commit()
        return True

    def get_pesticide_substances(self, pesticide_id):
        """Получение действующих веществ для конкретного пестицида"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT 
                pas.pesticide_id,
                pas.substance_id,
                pas.concentration,
                as.substance_name
            FROM pesticide_active_substances pas
            JOIN active_substances as ON pas.substance_id = as.id
            WHERE pas.pesticide_id = ?
            ORDER BY as.substance_name
        ''', (pesticide_id,))
        
        substances = []
        for row in cursor.fetchall():
            substances.append({
                'id': row['substance_id'],
                'name': row['substance_name'],
                'concentration': row['concentration']
            })
        
        return substances
    # ======= После обновления БД =========
    def get_pesticides_with_substances(self):
        """Получение пестицидов с их действующими веществами"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT 
                p.id,
                p.name,
                p.description,
                p.application_rate,
                p.packaging,
                p.price,
                p.manufacturer,
                pt.type_name as pesticide_type,
                GROUP_CONCAT(a.substance_name || ' ' || pas.concentration, '||') as substances
            FROM pesticides p
            LEFT JOIN pesticide_types pt ON p.pesticide_type_id = pt.id
            LEFT JOIN pesticide_active_substances pas ON p.id = pas.pesticide_id
            LEFT JOIN active_substances a ON pas.substance_id = a.id
            GROUP BY p.id
            ORDER BY p.name
        ''')
        
        # Преобразуем Row объекты в словари
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(dict(row))
        
        return result
    
    # def get_pesticide_substances(self, pesticide_id):
    #     """Получение действующих веществ препарата"""
    #     cursor = self.connection.cursor()
    #     cursor.execute('''
    #         SELECT 
    #             ps.id,
    #             a.substance_name as name,
    #             ps.concentration
    #         FROM pesticide_active_substances ps
    #         LEFT JOIN active_substances a ON ps.substance_id = a.id
    #         WHERE ps.pesticide_id = ?
    #     ''', (pesticide_id,))
        
    #     rows = cursor.fetchall()
    #     result = []
    #     for row in rows:
    #         result.append(dict(row))
        
    #     return result

    def get_pesticide_with_substances(self, pesticide_id):
        """Получение конкретного пестицида с его действующими веществами"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT 
                p.*,
                pt.type_name as pesticide_type,
                a.substance_name,
                pas.concentration
            FROM pesticides p
            LEFT JOIN pesticide_types pt ON p.pesticide_type_id = pt.id
            LEFT JOIN pesticide_active_substances pas ON p.id = pas.pesticide_id
            LEFT JOIN active_substances a ON pas.substance_id = a.id
            WHERE p.id = ?
        ''', (pesticide_id,))
        
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(dict(row))
        
        return result
    
def search_pesticides(self, query, filters=None):
    """Поиск препаратов с фильтрами"""
    cursor = self.connection.cursor()
    
    sql = '''
        SELECT DISTINCT p.*
        FROM pesticides p
        LEFT JOIN pesticide_active_substances pas ON p.id = pas.pesticide_id
        LEFT JOIN active_substances as ON pas.substance_id = as.id
        LEFT JOIN pesticide_diseases pd ON p.id = pd.pesticide_id
        LEFT JOIN diseases d ON pd.disease_id = d.id
        WHERE (p.name LIKE ? OR as.substance_name LIKE ? OR d.disease_name LIKE ?)
    '''
    params = [f'%{query}%', f'%{query}%', f'%{query}%']
    
    cursor.execute(sql, params)
    return cursor.fetchall()
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()

def _load_disease_classes_from_file(self):
    """Загрузка классов заболеваний из TXT файла"""
    try:
        # Путь к файлу с классами
        classes_file = self.database_path.parent / "disease_classes.txt"
        
        if not classes_file.exists():
            print("⚠️ Файл disease_classes.txt не найден, используются классы по умолчанию")
            self._create_default_disease_classes()
            return
        
        cursor = self.connection.cursor()
        
        # Очищаем таблицу перед загрузкой новых данных
        cursor.execute('DELETE FROM disease_classes')
        
        # Читаем файл
        with open(classes_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Пропускаем пустые строки и комментарии
                    parts = line.split(' ', 1)  # Разделяем по первому пробелу
                    if len(parts) == 2:
                        class_index = int(parts[0])
                        class_name = parts[1].replace('_', ' ')  # Заменяем подчеркивания на пробелы
                        
                        cursor.execute('''
                            INSERT INTO disease_classes (class_index, class_name)
                            VALUES (?, ?)
                        ''', (class_index, class_name))
        
        self.connection.commit()
        print(f"✅ Классы заболеваний загружены из файла: {classes_file.name}")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки классов заболеваний: {e}")
        self._create_default_disease_classes()

def _create_default_disease_classes(self):
    """Создание классов заболеваний по умолчанию"""
    try:
        cursor = self.connection.cursor()
        
        default_classes = [
            (0, 'Здоровое растение'),
            (1, 'Мучнистая роса'),
            (2, 'Парша'),
            (3, 'Ржавчина'),
            (4, 'Фитофтороз'),
            (5, 'Антракноз'),
            (6, 'Бактериальная пятнистость'),
            (7, 'Вирус мозаики')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO disease_classes (class_index, class_name)
            VALUES (?, ?)
        ''', default_classes)
        
        self.connection.commit()
        print("✅ Созданы классы заболеваний по умолчанию")
        
    except Exception as e:
        print(f"❌ Ошибка создания классов по умолчанию: {e}")


def export_disease_classes_to_file(self):
    """Экспорт классов заболеваний в TXT файл"""
    try:
        classes_file = self.database_path.parent / "disease_classes_export.txt"
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT class_index, class_name FROM disease_classes ORDER BY class_index')
        classes = cursor.fetchall()
        
        with open(classes_file, 'w', encoding='utf-8') as f:
            for class_item in classes:
                # Заменяем пробелы на подчеркивания для удобства
                class_name = class_item[1].replace(' ', '_')
                f.write(f"{class_item[0]} {class_name}\n")
        
        print(f"✅ Классы заболеваний экспортированы в: {classes_file.name}")
        return str(classes_file)
        
    except Exception as e:
        print(f"❌ Ошибка экспорта классов: {e}")
        return None

```

### app\core\database_backup.py
**Размер:** 18010 байт  
```python
"""
БАЗА ДАННЫХ - ТЕСТОВАЯ ВЕРСИЯ С ДАННЫМИ
Используется только с main_db_test.py
"""

import sqlite3
from pathlib import Path
from app.core.test_data import get_test_data

class DatabaseManagerBackup:
    """Менеджер базы данных SQLite - ТЕСТОВАЯ ВЕРСИЯ С ДАННЫМИ"""
    
    def __init__(self):
        # Прямой путь к БД
        base_dir = Path(__file__).parent.parent.parent
        self.database_path = base_dir / "app" / "assets" / "database" / "plant_protection.db"
        self.connection = None
        
        # Создаем директорию если не существует
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
    
    def initialize(self):
        """Инициализация базы данных с тестовыми данными"""
        try:
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row
            self._create_tables()
            self._insert_test_data()  # Используем тестовые данные
            print("✅ База данных инициализирована с тестовыми данными")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            return False
    
    def _create_tables(self):
        """Создание таблиц базы данных"""
        cursor = self.connection.cursor()
        
        # Все таблицы (копия из database.py)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cultures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                culture_name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # 3. Таблица действующих веществ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_substances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                substance_name TEXT NOT NULL UNIQUE
            )
        ''')
        
 # 4. Таблица классов заболеваний для нейросети (упрощенная)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_classes (
                class_index INTEGER PRIMARY KEY,
                class_name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # 5. Таблица болезней растений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT NOT NULL UNIQUE,
            symptoms TEXT,
            prevention_methods TEXT,
            culture_id INTEGER REFERENCES cultures(id),
            disease_class_index INTEGER REFERENCES disease_classes(class_index)
        )
    ''')
        
        # 6. Таблица пестицидов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                application_rate TEXT,
                packaging TEXT,
                price DECIMAL(10, 2),
                manufacturer TEXT,
                unit_of_measure TEXT,
                image_url TEXT,
                pesticide_type_id INTEGER REFERENCES pesticide_types(id)
            )
        ''')
        
        # 7. Связующие таблицы
        
        # Пестициды - Действующие вещества
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_active_substances (
                pesticide_id INTEGER REFERENCES pesticides(id),
                substance_id INTEGER REFERENCES active_substances(id),
                concentration TEXT,
                PRIMARY KEY (pesticide_id, substance_id)
            )
        ''')
        
        # Пестициды - Культуры
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_cultures (
                pesticide_id INTEGER REFERENCES pesticides(id),
                culture_id INTEGER REFERENCES cultures(id),
                PRIMARY KEY (pesticide_id, culture_id)
            )
        ''')
        
        # Пестициды - Болезни
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_diseases (
                pesticide_id INTEGER REFERENCES pesticides(id),
                disease_id INTEGER REFERENCES diseases(id),
                PRIMARY KEY (pesticide_id, disease_id)
            )
        ''')
        
        # 8. Таблица клиентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                total_orchard_area DECIMAL(10, 2),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 9. Таблица культур клиента
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_cultures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER REFERENCES clients(id),
                culture_id INTEGER REFERENCES cultures(id),
                area DECIMAL(10, 2),
                UNIQUE(client_id, culture_id)
            )
        ''')
        
        # 10. Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE,
                client_id INTEGER REFERENCES clients(id),
                order_date DATE NOT NULL,
                shipment_date DATE,
                payment_date DATE,
                total_amount DECIMAL(12, 2),
                status TEXT DEFAULT 'черновик',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 11. Таблица позиций заказа
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
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
        
        self.connection.commit()
        print("✅ Таблицы базы данных созданы")
        # Загружаем классы заболеваний из файла
        self._load_disease_classes_from_file()
    
    def _insert_test_data(self):
        """Вставка ТЕСТОВЫХ данных из test_data.py"""
        cursor = self.connection.cursor()
        
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM pesticides")
        if cursor.fetchone()[0] == 0:
            print("📝 Добавляем ТЕСТОВЫЕ данные...")
            
            test_data = get_test_data()
            
            # 1. Классы заболеваний
            cursor.executemany('''
                INSERT INTO disease_classes (class_index, class_name, description, is_active)
                VALUES (?, ?, ?, ?)
            ''', test_data['disease_classes'])
            
            # 2. Культуры
            for culture in test_data['cultures']:
                cursor.execute('INSERT INTO cultures (culture_name) VALUES (?)', (culture,))
            
            # 3. Типы пестицидов
            for p_type in test_data['pesticide_types']:
                cursor.execute('INSERT INTO pesticide_types (type_name) VALUES (?)', (p_type,))
            
            # 4. Действующие вещества
            for substance in test_data['substances']:
                cursor.execute('INSERT INTO active_substances (substance_name) VALUES (?)', (substance,))
            
            # 5. Болезни
            cursor.executemany('''
                INSERT INTO diseases (disease_name, symptoms, culture_id, disease_class_id) 
                VALUES (?, ?, ?, ?)
            ''', test_data['diseases'])
            
            # 6. Пестициды
            cursor.executemany('''
                INSERT INTO pesticides (name, description, application_rate, packaging, price, manufacturer, unit_of_measure, pesticide_type_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', test_data['pesticides'])
            
            # 7. Связи пестицидов с веществами
            cursor.executemany('''
                INSERT INTO pesticide_active_substances (pesticide_id, substance_id, concentration)
                VALUES (?, ?, ?)
            ''', test_data['pesticide_substances'])
            
            # 8. Связи пестицидов с культурами
            cursor.executemany('''
                INSERT INTO pesticide_cultures (pesticide_id, culture_id)
                VALUES (?, ?)
            ''', test_data['pesticide_cultures'])
            
            # 9. Связи пестицидов с болезнями
            cursor.executemany('''
                INSERT INTO pesticide_diseases (pesticide_id, disease_id)
                VALUES (?, ?)
            ''', test_data['pesticide_diseases'])
            
            # 10. Клиенты
            cursor.executemany('''
                INSERT INTO clients (client_name, contact_person, phone, email, total_orchard_area, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', test_data['clients'])
            
            self.connection.commit()
            print("✅ Тестовые данные добавлены")

    # Методы для работы с данными
    
    def get_disease_class_by_index(self, class_index):
        """Получение класса заболевания по индексу нейросети"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM disease_classes 
            WHERE class_index = ?
        ''', (class_index,))
        return cursor.fetchone()

    def get_all_disease_classes(self):
        """Получение всех классов заболеваний"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM disease_classes 
            ORDER BY class_index
        ''')
        return cursor.fetchall()

    def update_disease_classes_from_file(self):
        """Обновление классов заболеваний из файла"""
        print("🔄 Обновление классов заболеваний...")
        self._load_disease_classes_from_file()
        return True
    
    def get_recommendations_for_disease_class(self, class_index):
        """Получение рекомендаций для класса заболевания"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT p.* FROM pesticides p
            JOIN pesticide_diseases pd ON p.id = pd.pesticide_id
            JOIN diseases d ON pd.disease_id = d.id
            WHERE d.disease_class_id = ?
            LIMIT 10
        ''', (class_index,))
        return cursor.fetchall()
    
    
    def search_pesticides(self, query, filters=None):
        """Поиск препаратов - для тестовой версии"""
        try:
            cursor = self.connection.cursor()
            
            sql = '''
                SELECT p.*, pt.type_name 
                FROM pesticides p
                LEFT JOIN pesticide_types pt ON p.pesticide_type_id = pt.id
                WHERE p.name LIKE ? OR p.description LIKE ?
            '''
            params = [f'%{query}%', f'%{query}%']
            
            cursor.execute(sql, params)
            return cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return []
    
    def get_all_pesticides(self):
        """Получить все препараты - для тестовой версии"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT p.*, pt.type_name 
                FROM pesticides p
                LEFT JOIN pesticide_types pt ON p.pesticide_type_id = pt.id
                ORDER BY p.name
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка получения препаратов: {e}")
            return []
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()


def export_disease_classes_to_file(self):
    """Экспорт классов заболеваний в TXT файл"""
    try:
        classes_file = self.database_path.parent / "disease_classes_export.txt"
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT class_index, class_name FROM disease_classes ORDER BY class_index')
        classes = cursor.fetchall()
        
        with open(classes_file, 'w', encoding='utf-8') as f:
            for class_item in classes:
                # Заменяем пробелы на подчеркивания для удобства
                class_name = class_item[1].replace(' ', '_')
                f.write(f"{class_item[0]} {class_name}\n")
        
        print(f"✅ Классы заболеваний экспортированы в: {classes_file.name}")
        return str(classes_file)
        
    except Exception as e:
        print(f"❌ Ошибка экспорта классов: {e}")
        return None

def _load_disease_classes_from_file(self):
    """Загрузка классов заболеваний из TXT файла"""
    try:
        # Путь к файлу с классами
        classes_file = self.database_path.parent / "disease_classes.txt"
        
        if not classes_file.exists():
            print("⚠️ Файл disease_classes.txt не найден, используются классы по умолчанию")
            self._create_default_disease_classes()
            return
        
        cursor = self.connection.cursor()
        
        # Очищаем таблицу перед загрузкой новых данных
        cursor.execute('DELETE FROM disease_classes')
        
        # Читаем файл
        with open(classes_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Пропускаем пустые строки и комментарии
                    parts = line.split(' ', 1)  # Разделяем по первому пробелу
                    if len(parts) == 2:
                        class_index = int(parts[0])
                        class_name = parts[1].replace('_', ' ')  # Заменяем подчеркивания на пробелы
                        
                        cursor.execute('''
                            INSERT INTO disease_classes (class_index, class_name)
                            VALUES (?, ?)
                        ''', (class_index, class_name))
        
        self.connection.commit()
        print(f"✅ Классы заболеваний загружены из файла: {classes_file.name}")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки классов заболеваний: {e}")
        self._create_default_disease_classes()

def _create_default_disease_classes(self):
    """Создание классов заболеваний по умолчанию"""
    try:
        cursor = self.connection.cursor()
        
        default_classes = [
            (0, 'Здоровое растение'),
            (1, 'Мучнистая роса'),
            (2, 'Парша'),
            (3, 'Ржавчина'),
            (4, 'Фитофтороз'),
            (5, 'Антракноз'),
            (6, 'Бактериальная пятнистость'),
            (7, 'Вирус мозаики')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO disease_classes (class_index, class_name)
            VALUES (?, ?)
        ''', default_classes)
        
        self.connection.commit()
        print("✅ Созданы классы заболеваний по умолчанию")
        
    except Exception as e:
        print(f"❌ Ошибка создания классов по умолчанию: {e}")
```

### app\ml\model_loader.py
**Размер:** 2537 байт  
```python
import tensorflow as tf
import numpy as np

class ModelLoader:
    """Класс для загрузки и использования моделей TensorFlow Lite"""
    
    def __init__(self):
        self.model = None
        self.input_details = None
        self.output_details = None
    
    def load_model(self, model_path):
        """Загрузка модели TFLite"""
        try:
            # Загрузка модели
            self.model = tf.lite.Interpreter(model_path=model_path)
            self.model.allocate_tensors()
            
            # Получение информации о входе и выходе
            self.input_details = self.model.get_input_details()
            self.output_details = self.model.get_output_details()
            
            print("✅ Модель успешно загружена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            return False
    
    def predict(self, input_data):
        """Выполнение предсказания на входных данных"""
        try:
            if self.model is None:
                raise ValueError("Модель не загружена")
            
            # Установка входных данных
            self.model.set_tensor(self.input_details[0]['index'], input_data.astype(np.float32))
            
            # Выполнение инференса
            self.model.invoke()
            
            # Получение результатов
            output_data = self.model.get_tensor(self.output_details[0]['index'])
            
            return output_data
            
        except Exception as e:
            print(f"❌ Ошибка предсказания: {e}")
            return None
    
    def get_top_predictions(self, predictions, top_k=3):
        """Получение топ-K предсказаний"""
        try:
            # Получение индексов топ-K предсказаний
            top_indices = np.argsort(predictions[0])[-top_k:][::-1]
            top_probabilities = predictions[0][top_indices]
            
            return list(zip(top_indices, top_probabilities))
            
        except Exception as e:
            print(f"❌ Ошибка получения топ предсказаний: {e}")
            return []
```

### app\ui\__init__.py
**Размер:** 0 байт  
```python

```

### app\ui\screens\__init__.py
**Размер:** 0 байт  
```python

```

### app\ui\screens\catalog_screen.py
**ЦЕЛЕВОЙ ФАЙЛ**  
**Размер:** 85146 байт  
**Импортирует:** `kivy, kivymd`  
```python
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivymd.app import MDApp

Builder.load_string('''
<CatalogTab>:
    name: 'catalog'
    text: 'Каталог'
    icon: 'view-list'
    
    MDBoxLayout:
        orientation: 'vertical'
        
        # Панель поиска и сортировки
        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_height: True
            padding: '10dp'
            spacing: '10dp'
            
            MDIconButton:
                icon: 'sort'
                theme_icon_color: "Custom"
                icon_color: "green"
                size_hint: None, None
                size: "40dp", "40dp"
                on_release: root.open_sort_menu()

            # Строка поиска с крестиком
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.6
                spacing: '5dp'
                height: self.minimum_height
                
                MDTextField:
                    id: search_input
                    hint_text: "Поиск ..."
                    mode: "rectangle"
                    size_hint_x: 0.85
                    on_text: root.search_pesticides(self.text)
                
                MDIconButton:
                    icon: 'close-circle'
                    theme_icon_color: "Custom"
                    icon_color: "gray" if root.ids.search_input.text else [0.5, 0.5, 0.5, 0.3]
                    size_hint: None, None
                    size: "40dp", "40dp"
                    on_release: 
                        root.ids.search_input.text = ""
                        root.search_pesticides("")
            
            MDIconButton:
                icon: 'close-circle'
                theme_icon_color: "Custom"
                icon_color: "gray"
                size_hint: None, None
                size: "40dp", "40dp"
                on_release: root.clear_search()
            
            MDIconButton:
                icon: 'filter'
                theme_icon_color: "Custom"
                icon_color: "green"
                size_hint: None, None
                size: "40dp", "40dp"
                on_release: root.open_filters_menu()        

        # Список препаратов
        ScrollView:
            MDList:
                id: pesticides_list
                padding: '10dp'
                spacing: '10dp'
    # Фиксированная кнопка создания поверх списка
    MDFloatingActionButton:
        icon: "plus"
        type: "standard"
        md_bg_color: "green"
        elevation_normal: 12
        pos_hint: {"center_x": 0.5, "y": 0.02}
        size_hint: (None, None)
        size: ("56dp", "56dp")
        on_release: root.create_new_pesticide()

<PesticideCard>:
    orientation: 'vertical'
    padding: '12dp'
    spacing: '6dp'
    size_hint_y: None
    height: '120dp'
    ripple_behavior: True
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: '12dp'
        size_hint_y: 1
        
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.7
            spacing: '4dp'
            
            MDLabel:
                id: name_label
                text: root.pesticide_name
                font_style: 'H6'
                theme_text_color: 'Primary'
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'left'
                valign: 'top'
                shorten: True
                shorten_from: 'right'
                max_lines: 1
            
            MDLabel:
                id: substance_label
                text: f"ДВ: {root.pesticide_substance}"
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'left'
                valign: 'top'
                shorten: True
                shorten_from: 'right'
                max_lines: 1
            
            MDLabel:
                id: description_label
                text: root.pesticide_description
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'left'
                valign: 'top'
                shorten: True
                shorten_from: 'right'
                max_lines: 2
        
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.3
            spacing: '4dp'
            padding: '0dp', '4dp', '0dp', '0dp'
            
            MDLabel:
                id: price_label
                text: root.pesticide_price
                font_style: 'H6'
                theme_text_color: 'Primary'
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'right'
                valign: 'top'
            
            MDLabel:
                id: packaging_label
                text: f"{root.pesticide_packaging} | {root.pesticide_application_rate}"
                font_style: 'Caption'
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'right'
                valign: 'top'
                shorten: True
                shorten_from: 'right'
                max_lines: 2

<FilterDialog>:
    orientation: "vertical"
    spacing: "15dp"
    padding: "20dp"
    size_hint_y: None
    height: "500dp"
    
    ScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            spacing: '10dp'
            size_hint_y: None
            height: '380dp'
            
            MDLabel:
                text: "Тип пестицида:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: type_filter
                hint_text: "Выберите типы..."
                mode: "rectangle"
                on_focus: if self.focus: root.catalog_instance.open_type_menu()
            
            # Культуры
            MDLabel:
                text: "Культуры:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: culture_filter
                hint_text: "Выберите культуры..."
                mode: "rectangle"
                on_focus: if self.focus: root.catalog_instance.open_culture_menu()
            
            # Заболевания
            MDLabel:
                text: "Заболевания:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: disease_filter
                hint_text: "Выберите заболевания..."
                mode: "rectangle"
                on_focus: if self.focus: root.catalog_instance.open_disease_menu()
            
            # Цена    
            MDLabel:
                text: "Цена от:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: '10dp'
                size_hint_y: None
                height: '48dp'
                
                MDTextField:
                    id: min_price
                    hint_text: "0"
                    mode: "rectangle"
                    input_filter: 'float'
                
                MDLabel:
                    text: "до"
                    size_hint_x: None
                    width: '30dp'
                
                MDTextField:
                    id: max_price
                    hint_text: "10000"
                    mode: "rectangle"
                    input_filter: 'float'
    
    MDBoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "10dp"
        
        MDFlatButton:
            text: "Сбросить"
            on_release: root.reset_filters()
        
        MDRaisedButton:
            text: "Применить"
            on_release: root.apply_filters()

<SortDialog>:
    orientation: "vertical"
    spacing: "15dp"
    padding: "20dp"
    size_hint_y: None
    height: "300dp"
    
    MDLabel:
        text: "Сортировать по:"
        font_style: "H6"
        halign: "center"
        size_hint_y: None
        height: self.texture_size[1]
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: '10dp'
        
        MDLabel:
            text: "Критерий сортировки:"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: '20dp'
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: '5dp'
                
                MDLabel:
                    text: "Цена"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDCheckbox:
                    group: 'sort_criteria'
                    id: sort_price
                    on_active: root.set_sort_criteria('price')
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: '5dp'
                
                MDLabel:
                    text: "Название"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDCheckbox:
                    group: 'sort_criteria'
                    id: sort_name
                    on_active: root.set_sort_criteria('name')
        
        MDLabel:
            text: "Порядок сортировки:"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: '20dp'
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: '5dp'
                
                MDLabel:
                    text: "По возрастанию"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDCheckbox:
                    group: 'sort_order'
                    id: sort_asc
                    on_active: root.set_sort_order('asc')
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: '5dp'
                
                MDLabel:
                    text: "По убыванию"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDCheckbox:
                    group: 'sort_order'
                    id: sort_desc
                    on_active: root.set_sort_order('desc')
    
    MDBoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "10dp"
        
        MDFlatButton:
            text: "Отмена"
            on_release: root.cancel_sort()
        
        MDRaisedButton:
            text: "Применить"
            on_release: root.apply_sort()

<EditPesticideDialog>:
    orientation: "vertical"
    spacing: "15dp"
    padding: "20dp"
    size_hint_y: None
    height: "600dp"
    
    ScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            spacing: '15dp'
            size_hint_y: None
            height: self.minimum_height
            padding: '10dp'
            
            # Название препарата
            MDLabel:
                text: "Название:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_name
                # hint_text: "Название препарата"
                mode: "rectangle"
            
            # Действующее вещество
            MDLabel:
                text: "Действующее вещество:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_substance
                # hint_text: "Действующее вещество"
                mode: "rectangle"
                    
            MDRectangleFlatButton:
                id: edit_substances_btn
                text: "Редактировать ДВ"
                size_hint_x: 1
                on_release: app.root.show_substance_editor(pesticide_id)
            
            # Описание
            MDLabel:
                text: "Описание:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_description
                # hint_text: "Описание препарата"
                mode: "rectangle"
                multiline: True
                height: dp(80)
            
            # Норма расхода
            MDLabel:
                text: "Норма расхода:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_application_rate
                # hint_text: "Норма расхода"
                mode: "rectangle"
            
            # Фасовка
            MDLabel:
                text: "Фасовка:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_packaging
                # hint_text: "Фасовка"
                mode: "rectangle"
            
            # Цена
            MDLabel:
                text: "Цена:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_price
                # hint_text: "Цена"
                mode: "rectangle"
                input_filter: 'float'
            
            # Производитель
            MDLabel:
                text: "Производитель:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_manufacturer
                # hint_text: "Производитель"
                mode: "rectangle"

            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 1
                
                MDLabel:
                    text: "Действующие вещества:"
                    size_hint_x: 0.4
                    halign: 'right'
                    valign: 'middle'
                
                MDRectangleFlatButton:
                    id: edit_substances_btn
                    text: "Редактировать"
                    size_hint_x: 0.6
                    on_release: app.show_substance_editor(pesticide_id)
                    
            # Тип пестицида (выпадающий список)
            MDLabel:
                text: "Тип пестицида:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_type
                hint_text: "Выберите тип..."
                mode: "rectangle"
                on_focus: if self.focus: root.open_type_menu()
            
            # Болезни (многострочное поле)
            MDLabel:
                text: "Болезни:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_diseases
                hint_text: "Болезни (через запятую)"
                mode: "rectangle"
                multiline: True
                height: dp(60)
            
            # Культуры (многострочное поле)
            MDLabel:
                text: "Культуры:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: edit_cultures
                hint_text: "Культуры (через запятую)"
                mode: "rectangle"
                multiline: True
                height: dp(60)
    
    MDBoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "10dp"
        
        MDRaisedButton:
            text: "Удалить"
            theme_text_color: "Custom"
            text_color: "white"
            md_bg_color: "red"
            on_release: root.delete_pesticide()
        
        MDFlatButton:
            text: "Отмена"
            on_release: root.cancel_edit()
        
        MDRaisedButton:
            text: "Сохранить"
            on_release: root.save_pesticide()
''')


class PesticideCard(MDCard):
    pesticide_name = StringProperty("")
    pesticide_substance = StringProperty("")
    pesticide_description = StringProperty("")
    pesticide_price = StringProperty("")
    pesticide_packaging = StringProperty("")
    pesticide_application_rate = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_pesticide_name(self, instance, value):
        # Если название пустое, показываем "Без названия"
        if not value:
            self.ids.name_label.text = "Без названия"
        else:
            self.ids.name_label.text = value
    
    def on_pesticide_substance(self, instance, value):
        # Если ДВ пустое, не показываем "ДВ:"
        if not value:
            self.ids.substance_label.text = ""
        else:
            self.ids.substance_label.text = f"ДВ: {value}"
    
    def on_pesticide_description(self, instance, value):
        # Если описание пустое, не показываем ничего
        if not value:
            self.ids.description_label.text = ""
        else:
            self.ids.description_label.text = value
    
    def on_pesticide_price(self, instance, value):
        # Если цена пустая, показываем "Цена не указана"
        if not value:
            self.ids.price_label.text = "Цена не указана"
            self.ids.price_label.font_style = 'Body2'
            self.ids.price_label.theme_text_color = 'Secondary'
        else:
            self.ids.price_label.text = value
            self.ids.price_label.font_style = 'H6'
            self.ids.price_label.theme_text_color = 'Primary'
    
    def on_pesticide_packaging(self, instance, value):
        self._update_packaging_text()
    
    def on_pesticide_application_rate(self, instance, value):
        self._update_packaging_text()
    
    def _update_packaging_text(self):
        """Обновить текст фасовки и нормы расхода"""
        packaging = self.pesticide_packaging
        rate = self.pesticide_application_rate
        
        if packaging and rate:
            self.ids.packaging_label.text = f"{packaging} | {rate}"
        elif packaging:
            self.ids.packaging_label.text = packaging
        elif rate:
            self.ids.packaging_label.text = f"Норма: {rate}"
        else:
            self.ids.packaging_label.text = ""

class FilterDialog(MDBoxLayout):
    def __init__(self, apply_callback, reset_callback, catalog_instance, current_filters, **kwargs):
        super().__init__(**kwargs)
        self.apply_callback = apply_callback
        self.reset_callback = reset_callback
        self.catalog_instance = catalog_instance
        self.current_filters = current_filters
        
        # Восстанавливаем предыдущие значения фильтров
        if current_filters:
            if 'type' in current_filters and current_filters['type']:
                self.ids.type_filter.text = ', '.join(current_filters['type'])
            if 'cultures' in current_filters and current_filters['cultures']:
                self.ids.culture_filter.text = ', '.join(current_filters['cultures'])
            if 'diseases' in current_filters and current_filters['diseases']:
                self.ids.disease_filter.text = ', '.join(current_filters['diseases'])
            if 'min_price' in current_filters:
                self.ids.min_price.text = current_filters['min_price']
            if 'max_price' in current_filters:
                self.ids.max_price.text = current_filters['max_price']
    
    def apply_filters(self):
        self.apply_callback()
    
    def reset_filters(self):
        self.reset_callback()


class SortDialog(MDBoxLayout):
    def __init__(self, apply_callback, cancel_callback, current_sort, **kwargs):
        super().__init__(**kwargs)
        self.apply_callback = apply_callback
        self.cancel_callback = cancel_callback
        self.sort_criteria = current_sort.get('criteria', 'name')
        self.sort_order = current_sort.get('order', 'asc')
        
        # Устанавливаем текущие значения
        if self.sort_criteria == 'price':
            self.ids.sort_price.active = True
        else:
            self.ids.sort_name.active = True
            
        if self.sort_order == 'asc':
            self.ids.sort_asc.active = True
        else:
            self.ids.sort_desc.active = True
    
    def set_sort_criteria(self, criteria):
        self.sort_criteria = criteria
    
    def set_sort_order(self, order):
        self.sort_order = order
    
    def apply_sort(self):
        self.apply_callback(self.sort_criteria, self.sort_order)
    
    def cancel_sort(self):
        self.cancel_callback()

class EditPesticideDialog(MDBoxLayout):
    def __init__(self, catalog_instance, pesticide_data=None, save_callback=None, 
                 delete_callback=None, cancel_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.catalog_instance = catalog_instance
        self.pesticide_data = pesticide_data or {}  # ЗДЕСЬ ИСПРАВЛЕНИЕ - инициализируем
        self.save_callback = save_callback
        self.delete_callback = delete_callback
        self.cancel_callback = cancel_callback
        self.type_menu = None
        
        # Определяем, это новый препарат или редактирование
        self.is_new = not self.pesticide_data.get('name', '')
    
    def on_kv_post(self, base_widget):
        """Вызывается после загрузки KV-разметки"""
        super().on_kv_post(base_widget)
        
        # Проверяем, есть ли у нас доступ к ids
        if hasattr(self, 'ids'):
            # Заполняем поля данными препарата
            self.ids.edit_name.text = self.pesticide_data.get('name', '')
            self.ids.edit_substance.text = self.pesticide_data.get('substance', '')
            self.ids.edit_description.text = self.pesticide_data.get('description', '')
            self.ids.edit_application_rate.text = self.pesticide_data.get('application_rate', '')
            self.ids.edit_packaging.text = self.pesticide_data.get('packaging', '')
            
            # Для цены (убираем лишние "руб.")
            price_text = str(self.pesticide_data.get('price', ''))
            if 'руб' in price_text:
                price_text = price_text.replace(' руб.', '').replace(' ', '')
            self.ids.edit_price.text = price_text
            
            self.ids.edit_manufacturer.text = self.pesticide_data.get('manufacturer', '')
            self.ids.edit_type.text = self.pesticide_data.get('type', 'Гербициды')
            self.ids.edit_diseases.text = self.pesticide_data.get('diseases', '')
            self.ids.edit_cultures.text = self.pesticide_data.get('cultures', '')
    
    def open_type_menu(self):
        """Открыть меню выбора типа пестицида ПОД полем"""
        try:
            # Если меню уже открыто, закройте его
            if self.type_menu and self.type_menu.parent:
                self.type_menu.dismiss()
                self.type_menu = None
                return
            
            # Список доступных типов пестицидов
            pesticide_types = ["Гербициды", "Инсектициды", "Фунгициды", "Бактерициды", "Фумиганты"]
            
            # Создаем элементы меню
            menu_items = [
                {
                    "text": p_type,
                    "viewclass": "OneLineListItem",
                    "height": dp(48),
                    "on_release": lambda x=p_type: self.select_pesticide_type(x),
                } for p_type in pesticide_types
            ]
            
            # Создаем меню ПОД полем
            self.type_menu = MDDropdownMenu(
                caller=self.ids.edit_type,
                items=menu_items,
                width=self.ids.edit_type.width * 1.5,  # Ширина относительно поля ввода
                max_height=dp(150),
                position="auto",
                ver_growth="down"
            )
            self.type_menu.open()
            
        except Exception as e:
            print(f"❌ Ошибка открытия меню типа: {e}")
    
    def select_pesticide_type(self, pesticide_type):
        """Выбрать тип пестицида"""
        try:
            self.ids.edit_type.text = pesticide_type
            if self.type_menu:
                self.type_menu.dismiss()
                self.type_menu = None
        except Exception as e:
            print(f"❌ Ошибка выбора типа: {e}")
    
    def save_pesticide(self):
        try:
            updated_data = {
                'name': self.ids.edit_name.text,
                'substance': self.ids.edit_substance.text,
                'description': self.ids.edit_description.text,
                'application_rate': self.ids.edit_application_rate.text,
                'packaging': self.ids.edit_packaging.text,
                'price': self.ids.edit_price.text,
                'manufacturer': self.ids.edit_manufacturer.text,
                'unit': self.ids.edit_unit.text,
                'type': self.ids.edit_type.text,
                'diseases': self.ids.edit_diseases.text,
                'cultures': self.ids.edit_cultures.text,
            }
            
            # Для существующего препарата добавляем ID
            if not self.is_new and 'id' in self.pesticide_data:
                updated_data['id'] = self.pesticide_data['id']
            
            self.save_callback(updated_data)
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            self.catalog_instance._show_error_message(f"Ошибка сохранения: {e}")
    
    def delete_pesticide(self):
        if self.delete_callback:
            self.delete_callback(self.pesticide_data)
    
    def cancel_edit(self):
        # Закрываем меню если открыто
        if self.type_menu:
            self.type_menu.dismiss()
            self.type_menu = None
        self.cancel_callback()
    
    def on_dismiss(self):
        """Закрыть меню при закрытии диалога"""
        if self.type_menu:
            self.type_menu.dismiss()
            self.type_menu = None


            
class CatalogTab(MDBottomNavigationItem):
    app = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Инициализация всех необходимых атрибутов
        if not self.app:
            self.app = MDApp.get_running_app()
        
        # Инициализация основных атрибутов
        self.filters = {}
        self.sort_settings = {'criteria': 'name', 'order': 'asc'}
        self.filter_dialog = None
        self.type_menu = None
        self.culture_menu = None
        self.disease_menu = None
        self.sort_dialog = None
        self.detail_dialog = None
        self.edit_dialog = None
        self.current_editing_pesticide = None
        self.selected_types = []
        self.selected_cultures = []
        self.selected_diseases = []
        
        # Инициализация test_pesticides (ЗДЕСЬ ИСПРАВЛЕНИЕ!)
        self.test_pesticides = self._get_test_pesticides()
    
    def on_enter(self):
        """Вызывается при переходе на вкладку"""
        self._setup_catalog()
    
    def _setup_catalog(self):
        """Настройка каталога"""
        self._load_pesticides()
    
    def clear_search(self):
        """Очистить поиск"""
        self.ids.search_input.text = ""
        self._load_pesticides()
        print("🔄 Поиск очищен")

    def on_search_text_change(self, instance, value):
        """Обновить цвет крестика при изменении текста поиска"""
        if hasattr(self, 'search_clear_button'):
            if value:
                self.search_clear_button.icon_color = "gray"
            else:
                self.search_clear_button.icon_color = [0.5, 0.5, 0.5, 0.3]
# ============= Новый метод ======
    def reset_filters_and_search(self):
        """Сбросить все фильтры и поиск"""
        # Сброс фильтров
        self.filters = {}
        self.selected_types = []
        self.selected_cultures = []
        self.selected_diseases = []
        
        # Сброс поиска
        self.ids.search_input.text = ""
        
        # Обновляем кнопку очистки поиска
        self.ids.search_clear_button.icon_color = [0.5, 0.5, 0.5, 0.3]
        
        # Сбрасываем текст в открытом диалоге фильтров (если он открыт)
        if self.filter_dialog:
            content = self.filter_dialog.content_cls
            content.ids.type_filter.text = ""
            content.ids.culture_filter.text = ""
            content.ids.disease_filter.text = ""
            content.ids.min_price.text = ""
            content.ids.max_price.text = ""
        
        print("🔄 Все фильтры и поиск сброшены")
        self._load_pesticides()
# ============= Новый метод ======
    def create_new_pesticide(self):
        """Создать новый препарат"""
        print("➕ Создание нового препарата")
        
        # Создаем пустые данные для нового препарата
        new_pesticide = {
            'id': len(self.test_pesticides) + 1,
            'name': '',
            'substance': '',
            'description': '',
            'application_rate': '',
            'packaging': '',
            'price': '',
            'manufacturer': '',
            'type': 'Гербициды',
            'cultures': '',
            'diseases': ''
        }
        
        self.current_editing_pesticide = new_pesticide
        
        # Создаем диалог редактирования
        self.edit_dialog = MDDialog(
            title="Создание нового препарата",
            type="custom",
            content_cls=EditPesticideDialog(
                catalog_instance=self,
                pesticide_data=new_pesticide,
                save_callback=self.save_new_pesticide,
                delete_callback=None,
                cancel_callback=self.cancel_edit
            ),
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        self.edit_dialog.open()

    def save_new_pesticide(self, new_data):
        """Сохранить новый препарат"""
        print(f"💾 Создан новый препарат: {new_data['name']}")
        
        try:
            # Закрываем меню если оно открыто
            if hasattr(self, 'edit_dialog') and self.edit_dialog:
                content = self.edit_dialog.content_cls
                if hasattr(content, 'type_menu') and content.type_menu:
                    content.type_menu.dismiss()

            # Добавляем ID и форматируем цену
            new_data['id'] = len(self.test_pesticides) + 1
            
            # Заполняем обязательные поля если они пустые
            if not new_data.get('name'):
                new_data['name'] = 'Новый препарат'
            
            if new_data.get('price'):
                if 'руб' not in str(new_data['price']):
                    new_data['price'] = f"{new_data['price']} руб."
            else:
                new_data['price'] = 'Цена не указана'
            
            if not new_data.get('unit'):
                new_data['unit'] = 'шт'
            if not new_data.get('type'):
                new_data['type'] = 'Гербициды'
            
            # Добавляем новый препарат в список
            self.test_pesticides.append(new_data)
            
            # Закрываем диалог редактирования
            if self.edit_dialog:
                self.edit_dialog.dismiss()
            
            # Обновляем список препаратов
            self._load_pesticides(
                search_query=self.ids.search_input.text,
                filters=self.filters
            )
            
            # Показываем сообщение об успехе
            self._show_success_message(f"Препарат '{new_data['name']}' создан")
            
        except Exception as e:
            print(f"❌ Ошибка создания: {e}")
            self._show_error_message(f"Ошибка создания: {e}")

    def _load_pesticides(self, search_query="", filters=None, sort_criteria=None, sort_order=None):
        """Загрузка препаратов с действующими веществами"""
        pesticides_list = self.ids.pesticides_list
        pesticides_list.clear_widgets()
        
        try:
            # Получаем препараты из БД
            app = MDApp.get_running_app()
            
            if hasattr(app.db, 'get_pesticides_with_substances'):
                pesticides = app.db.get_pesticides_with_substances()
            else:
                print("⚠️ Метод get_pesticides_with_substances не найден, используем тестовые данные")
                self._load_test_pesticides(search_query, filters, sort_criteria, sort_order)
                return
            
            # Применяем поиск и фильтры
            filtered_pesticides = self._apply_filters(pesticides, search_query, filters)
            
            # Применяем сортировку
            sorted_pesticides = self._apply_sorting(filtered_pesticides, sort_criteria, sort_order)

            # Добавляем препараты в список
            for pesticide in sorted_pesticides:
                card = PesticideCard()
                
                # Заполняем основные данные - используем прямое обращение к ключам
                card.pesticide_name = pesticide.get('name', '') if hasattr(pesticide, 'get') else (pesticide['name'] if 'name' in pesticide else '')
                card.pesticide_description = pesticide.get('description', '') if hasattr(pesticide, 'get') else (pesticide['description'] if 'description' in pesticide else '')
                
                # Форматируем цену
                price = ''
                if hasattr(pesticide, 'get'):
                    price = pesticide.get('price', '')
                elif 'price' in pesticide:
                    price = pesticide['price']
                
                if price and isinstance(price, (int, float)):
                    card.pesticide_price = f"{int(price)} руб."
                else:
                    card.pesticide_price = str(price) if price else 'Цена не указана'
                
                # Получаем другие поля
                packaging = pesticide.get('packaging', '') if hasattr(pesticide, 'get') else (pesticide['packaging'] if 'packaging' in pesticide else '')
                application_rate = pesticide.get('application_rate', '') if hasattr(pesticide, 'get') else (pesticide['application_rate'] if 'application_rate' in pesticide else '')
                
                card.pesticide_packaging = packaging
                card.pesticide_application_rate = application_rate
                
                # Формируем строку с действующими веществами
                substances_text = ""
                if hasattr(pesticide, 'get'):
                    substances = pesticide.get('substances')
                else:
                    substances = pesticide['substances'] if 'substances' in pesticide else None
                
                if substances:
                    substances_str = str(substances)
                    if substances_str and substances_str != 'None':
                        # Разделяем вещества по '||'
                        substances_list = substances_str.split('||')
                        for substance_info in substances_list:
                            if substance_info.strip():
                                # Форматируем: "Название (концентрация)"
                                parts = substance_info.strip().split(' ')
                                if len(parts) >= 2:
                                    name = parts[0]
                                    concentration = ' '.join(parts[1:])
                                    substances_text += f"• {name} ({concentration})\n"
                                else:
                                    substances_text += f"• {substance_info.strip()}\n"
                
                # Если вещества есть, показываем их, иначе показываем "Не указаны"
                if substances_text:
                    card.pesticide_substance = substances_text.strip()
                else:
                    card.pesticide_substance = "Действующие вещества не указаны"
                
                # Привязываем обработчик клика
                # Передаем словарь или Row объект как есть
                card.on_release = lambda p=pesticide: self.show_pesticide_details(p)
                
                pesticides_list.add_widget(card)
                
        except Exception as e:
            print(f"Ошибка загрузки препаратов: {e}")
            # Fallback на тестовые данные
            self._load_test_pesticides(search_query, filters, sort_criteria, sort_order)
    

    def _apply_filters(self, pesticides, search_query, filters):
        """Применение фильтров к списку препаратов"""
        filtered = pesticides
        
        # Преобразуем все элементы в словари для удобства
        processed_pesticides = []
        for p in filtered:
            if hasattr(p, 'get'):
                processed_pesticides.append(p)
            else:
                processed_pesticides.append(dict(p) if hasattr(p, '_asdict') else p)
        
        filtered = processed_pesticides
        
        # Поиск по названию, описанию и веществу
        if search_query:
            search_query = search_query.lower()
            filtered = [p for p in filtered
                    if search_query in p.get('name', '').lower()
                    or search_query in p.get('description', '').lower()
                    or search_query in str(p.get('substance', '')).lower()]
        
        # Фильтр по типу
        if filters and filters.get('type'):
            filtered = [p for p in filtered if p.get('type', '') in filters['type']]
        
        # Фильтр по культурам
        if filters and filters.get('cultures'):
            selected_cultures = filters['cultures']
            filtered = [p for p in filtered if any(
                culture in str(p.get('cultures', '')) 
                for culture in selected_cultures
            )]
        
        # Фильтр по заболеваниям
        if filters and filters.get('diseases'):
            selected_diseases = filters['diseases']
            filtered = [p for p in filtered if any(
                disease in str(p.get('diseases', '')) 
                for disease in selected_diseases
            )]
        
        # Фильтр по цене
        if filters:
            min_price = filters.get('min_price')
            max_price = filters.get('max_price')
            
            if min_price and min_price.strip():
                try:
                    min_val = float(min_price.replace(' ', ''))
                    filtered = [p for p in filtered if self._extract_price(p.get('price', 0)) >= min_val]
                except ValueError:
                    pass
            
            if max_price and max_price.strip():
                try:
                    max_val = float(max_price.replace(' ', ''))
                    filtered = [p for p in filtered if self._extract_price(p.get('price', 0)) <= max_val]
                except ValueError:
                    pass
        
        return filtered
    
    def _apply_sorting(self, pesticides, criteria=None, order=None):
        """Применение сортировки к списку препаратов"""
        if not criteria:
            criteria = self.sort_settings['criteria']
        if not order:
            order = self.sort_settings['order']
        
        reverse = (order == 'desc')
        
        if criteria == 'price':
            return sorted(pesticides, key=lambda x: self._extract_price(x['price']), reverse=reverse)
        else:  # name
            return sorted(pesticides, key=lambda x: x['name'], reverse=reverse)
    
    def search_pesticides(self, query):
        """Поиск препаратов"""
        print(f"🔍 Поиск: {query}")
        # Обновляем цвет крестика
        if hasattr(self, 'search_clear_button'):
            if query:
                self.search_clear_button.icon_color = "gray"
            else:
                self.search_clear_button.icon_color = [0.5, 0.5, 0.5, 0.3]
        
        self._load_pesticides(search_query=query, filters=self.filters)
    
    def open_sort_menu(self):
        """Открыть меню сортировки"""
        self.sort_dialog = MDDialog(
            title="Сортировка препаратов",
            type="custom",
            content_cls=SortDialog(
                apply_callback=self.apply_sort,
                cancel_callback=self.cancel_sort,
                current_sort=self.sort_settings
            ),
            size_hint=(0.8, None),
            height="350dp"
        )
        self.sort_dialog.open()
    
    def apply_sort(self, criteria, order):
        """Применить сортировку"""
        self.sort_settings = {'criteria': criteria, 'order': order}
        print(f"✅ Применена сортировка: {criteria} ({order})")
        self._load_pesticides(
            search_query=self.ids.search_input.text,
            filters=self.filters,
            sort_criteria=criteria,
            sort_order=order
        )
        if self.sort_dialog:
            self.sort_dialog.dismiss()
    
    def cancel_sort(self):
        """Отменить сортировку"""
        if self.sort_dialog:
            self.sort_dialog.dismiss()
    
    def open_filters_menu(self):
        """Открыть меню фильтров"""
        self.filter_dialog = MDDialog(
            title="Фильтры препаратов",
            type="custom",
            content_cls=FilterDialog(
                apply_callback=self.apply_filters,
                reset_callback=self.reset_filters,
                catalog_instance=self,
                current_filters=self.filters
            ),
            size_hint=(0.8, None),
            height="550dp"  # Увеличили высоту
        )
        self.filter_dialog.open()
    
    def open_type_menu(self):
        """Открыть меню выбора типа пестицида"""
        if not self.filter_dialog:
            return
        
        # Если меню уже открыто, закройте его
        if self.type_menu and self.type_menu.parent:
            self.type_menu.dismiss()
            self.type_menu = None
            return
        
        # Список доступных типов пестицидов
        pesticide_types = ["Гербициды", "Инсектициды", "Фунгициды", "Бактерициды", "Фумиганты"]
        
        # Создаем элементы меню
        menu_items = [
            {
                "text": p_type,
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda x=p_type: self.select_pesticide_type(x),
            } for p_type in pesticide_types
        ]
        
        # Создаем меню - список НАД полем
        self.type_menu = MDDropdownMenu(
            caller=self.filter_dialog.content_cls.ids.type_filter,  # Исправлено!
            items=menu_items,
            width=dp(200),  # Укажите фиксированную ширину
            max_height=dp(150),
            position="auto",
            ver_growth="down"
        )
        self.type_menu.open()

    def open_culture_menu(self):
        """Открыть меню выбора культур ПОД полем"""
        if not self.filter_dialog:
            return
        
        # Получаем уникальные культуры из препаратов
        all_cultures = []
        for pesticide in self.test_pesticides:
            if 'cultures' in pesticide:
                cultures = [c.strip() for c in pesticide['cultures'].split(',')]
                all_cultures.extend(cultures)
        
        unique_cultures = sorted(set([c for c in all_cultures if c]))
        
        # Если меню уже открыто, просто обновляем его
        if hasattr(self, 'culture_menu') and self.culture_menu and self.culture_menu.parent:
            self._update_culture_menu_items(unique_cultures)
            return
        
        # Создаем меню ПОД полем
        self.culture_menu = MDDropdownMenu(
            caller=self.filter_dialog.content_cls.ids.culture_filter,
            items=[],  # Заполним ниже
            width_mult=4,
            max_height=dp(200),
            position="auto",  # Авто-позиционирование
            ver_growth="down"  # Растет вниз
        )
        self._update_culture_menu_items(unique_cultures)
        self.culture_menu.open()

    def _update_culture_menu_items(self, cultures):
        """Обновить элементы меню культур"""
        culture_menu_items = []
        selected_cultures = getattr(self, 'selected_cultures', [])
        
        for culture in cultures:
            if not culture:  # Пропускаем пустые строки
                continue
                
            is_active = culture in selected_cultures
            display_text = f"✓ {culture}" if is_active else f"  {culture}"
            
            culture_menu_items.append({
                "viewclass": "OneLineListItem",
                "text": display_text,
                "height": dp(40),
                "on_release": lambda x=culture: self.toggle_culture(x),
                "bg_color": (0.95, 0.95, 0.95, 1) if is_active else (1, 1, 1, 1)
            })
        
        self.culture_menu.items = culture_menu_items

    def toggle_culture(self, culture):
        """Переключить выбор культуры"""
        if not hasattr(self, 'selected_cultures'):
            self.selected_cultures = []
        
        if culture in self.selected_cultures:
            self.selected_cultures.remove(culture)
        else:
            self.selected_cultures.append(culture)
        
        # Обновляем текст в поле фильтра
        if self.filter_dialog:
            self.filter_dialog.content_cls.ids.culture_filter.text = ', '.join(self.selected_cultures)
        
        # Обновляем фильтр
        if hasattr(self, 'filters'):
            self.filters['cultures'] = self.selected_cultures.copy()
        
        # Обновляем меню без закрытия
        all_cultures = []
        for pesticide in self.test_pesticides:
            if 'cultures' in pesticide:
                cultures = [c.strip() for c in pesticide['cultures'].split(',')]
                all_cultures.extend(cultures)
        
        unique_cultures = sorted(set([c for c in all_cultures if c]))
        self._update_culture_menu_items(unique_cultures)

    def open_disease_menu(self):
        """Открыть меню выбора заболеваний ПОД полем"""
        if not self.filter_dialog:
            return
        
        # Получаем уникальные заболевания из препаратов
        all_diseases = []
        for pesticide in self.test_pesticides:
            if 'diseases' in pesticide:
                diseases = [d.strip() for d in pesticide['diseases'].split(',')]
                all_diseases.extend(diseases)
        
        unique_diseases = sorted(set([d for d in all_diseases if d]))
        
        # Если меню уже открыто, просто обновляем его
        if hasattr(self, 'disease_menu') and self.disease_menu and self.disease_menu.parent:
            self._update_disease_menu_items(unique_diseases)
            return
        
        # Создаем меню ПОД полем
        self.disease_menu = MDDropdownMenu(
            caller=self.filter_dialog.content_cls.ids.disease_filter,
            items=[],  # Заполним ниже
            width_mult=4,
            max_height=dp(200),
            position="auto",  # Авто-позиционирование
            ver_growth="down"  # Растет вниз
        )
        self._update_disease_menu_items(unique_diseases)
        self.disease_menu.open()

    def _update_disease_menu_items(self, diseases):
        """Обновить элементы меню заболеваний"""
        disease_menu_items = []
        selected_diseases = getattr(self, 'selected_diseases', [])
        
        for disease in diseases:
            if not disease:  # Пропускаем пустые строки
                continue
                
            is_active = disease in selected_diseases
            display_text = f"✓ {disease}" if is_active else f"  {disease}"
            
            disease_menu_items.append({
                "viewclass": "OneLineListItem",
                "text": display_text,
                "height": dp(40),
                "on_release": lambda x=disease: self.toggle_disease(x),
                "bg_color": (0.95, 0.95, 0.95, 1) if is_active else (1, 1, 1, 1)
            })
        
        self.disease_menu.items = disease_menu_items

    def toggle_disease(self, disease):
        """Переключить выбор заболевания"""
        if not hasattr(self, 'selected_diseases'):
            self.selected_diseases = []
        
        if disease in self.selected_diseases:
            self.selected_diseases.remove(disease)
        else:
            self.selected_diseases.append(disease)
        
        # Обновляем текст в поле фильтра
        if self.filter_dialog:
            self.filter_dialog.content_cls.ids.disease_filter.text = ', '.join(self.selected_diseases)
        
        # Обновляем фильтр
        if hasattr(self, 'filters'):
            self.filters['diseases'] = self.selected_diseases.copy()
        
        # Обновляем меню без закрытия
        all_diseases = []
        for pesticide in self.test_pesticides:
            if 'diseases' in pesticide:
                diseases = [d.strip() for d in pesticide['diseases'].split(',')]
                all_diseases.extend(diseases)
        
        unique_diseases = sorted(set([d for d in all_diseases if d]))
        self._update_disease_menu_items(unique_diseases)

    def _update_type_menu_items(self):
        """Обновить элементы меню типов пестицидов"""
        if not hasattr(self, 'type_menu'):
            return
        
        # Список доступных типов пестицидов
        pesticide_types = ["Гербициды", "Инсектициды", "Фунгициды", "Бактерициды", "Фумиганты"]
        
        # Создаем элементы меню
        menu_items = [
            {
                "text": p_type,
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda x=p_type: self.select_pesticide_type(x),
            } for p_type in pesticide_types
        ]
        
        self.type_menu.items = menu_items

    def toggle_pesticide_type(self, pesticide_type):
        """Переключить выбор типа пестицида"""
        if pesticide_type in self.selected_types:
            self.selected_types.remove(pesticide_type)
        else:
            self.selected_types.append(pesticide_type)
        
        # Обновляем текст в поле фильтра
        if self.filter_dialog:
            self.filter_dialog.content_cls.ids.type_filter.text = ', '.join(self.selected_types)
        
        # Обновляем фильтр
        if hasattr(self, 'filters'):
            self.filters['type'] = self.selected_types.copy()
        
        # Обновляем меню без закрытия
        self._update_type_menu_items()
    
    def show_pesticide_details(self, pesticide):
        """Показать детали препарата с действующими веществами"""
        try:
            # Преобразуем pesticide в словарь если это Row объект
            if not hasattr(pesticide, 'get') and hasattr(pesticide, '__getitem__'):
                # Это уже словарь или что-то подобное
                pesticide_data = pesticide
            else:
                # Преобразуем Row в dict
                pesticide_data = dict(pesticide) if hasattr(pesticide, '_asdict') else pesticide
            
            print(f"📋 Детали препарата: {pesticide_data.get('name', 'Unknown')}")
            
            # Сохраняем ссылку на текущий препарат
            self.current_editing_pesticide = pesticide_data
            
            # Получаем полные данные с ДВ из БД
            app = MDApp.get_running_app()
            try:
                # Получаем препарат с веществами
                full_pesticide_data = app.db.get_pesticide_with_substances(pesticide_data['id'])
                if not full_pesticide_data:
                    full_pesticide_data = [pesticide_data]  # Fallback
            except Exception as e:
                print(f"❌ Ошибка получения полных данных: {e}")
                full_pesticide_data = [pesticide_data]
            
            # Формируем строку с действующими веществами
            substances_text = ""
            if len(full_pesticide_data) > 0:
                # Проверяем первый элемент на наличие substance_name
                first_item = full_pesticide_data[0]
                if hasattr(first_item, 'get'):
                    item_dict = first_item
                else:
                    item_dict = dict(first_item) if hasattr(first_item, '_asdict') else first_item
                
                if 'substance_name' in item_dict and item_dict['substance_name']:
                    for substance_item in full_pesticide_data:
                        if hasattr(substance_item, 'get'):
                            substance_dict = substance_item
                        else:
                            substance_dict = dict(substance_item) if hasattr(substance_item, '_asdict') else substance_item
                        
                        if substance_dict.get('substance_name') and substance_dict.get('concentration'):
                            substances_text += f"• {substance_dict['substance_name']} ({substance_dict['concentration']})\n"
                elif 'substances' in pesticide_data and pesticide_data['substances']:
                    # Альтернативный формат
                    substances_str = str(pesticide_data.get('substances', ''))
                    if substances_str and substances_str != 'None':
                        substances_list = substances_str.split('||')
                        for substance_info in substances_list:
                            if substance_info.strip():
                                substances_text += f"• {substance_info.strip()}\n"
            
            if not substances_text:
                substances_text = "Действующие вещества не указаны"
            
            # Получаем остальную информацию
            pesticide_type = pesticide_data.get('pesticide_type', pesticide_data.get('type', 'Не указано'))
            price = pesticide_data.get('price', '')
            
            if isinstance(price, (int, float)):
                price_display = f"{int(price)} руб."
            else:
                price_display = str(price) if price else 'Не указана'
            
            # Создаем детальную информацию
            detail_text = f"""[color=000000]
    [b]Действующие вещества:[/b]
    {substances_text}

    [b]Описание:[/b]
    {pesticide_data.get('description', 'Не указано')}

    [b]Норма расхода:[/b] {pesticide_data.get('application_rate', 'Не указано')}
    [b]Фасовка:[/b] {pesticide_data.get('packaging', 'Не указано')}
    [b]Цена:[/b] {price_display}
    [b]Производитель:[/b] {pesticide_data.get('manufacturer', 'Не указано')}

    [b]Тип пестицида:[/b] {pesticide_type}
    [/color]"""
            
            # Создаем кнопки
            buttons = [
                MDIconButton(
                    icon="close",
                    theme_icon_color="Custom",
                    icon_color="gray",
                    on_release=lambda x: self.detail_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Добавить в заказ",
                    on_release=lambda x: self.add_to_order(pesticide_data)
                )
            ]
            
            # Добавляем кнопку редактирования ДВ если у препарата есть ID
            if 'id' in pesticide_data:
                buttons.insert(1, MDIconButton(
                    icon="flask",
                    theme_icon_color="Custom",
                    icon_color="blue",
                    on_release=lambda x: self.app.show_substance_editor(pesticide_data['id'])
                ))
            
            self.detail_dialog = MDDialog(
                title=pesticide_data.get('name', 'Без названия'),
                text=detail_text.strip(),
                size_hint=(0.9, 0.8),
                buttons=buttons
            )
            self.detail_dialog.open()
            
        except Exception as e:
            print(f"❌ Ошибка отображения деталей препарата: {e}")
            self._show_error_message(f"Ошибка отображения деталей: {e}")

    def _load_test_pesticides(self, search_query="", filters=None, sort_criteria=None, sort_order=None):
        """Загрузка тестовых препаратов (fallback)"""
        pesticides_list = self.ids.pesticides_list
        pesticides_list.clear_widgets()
        
        # Используем self.test_pesticides
        test_pesticides = self.test_pesticides
        
        # Применяем поиск и фильтры
        filtered_pesticides = self._apply_filters(test_pesticides, search_query, filters)
        
        # Применяем сортировку
        sorted_pesticides = self._apply_sorting(filtered_pesticides, sort_criteria, sort_order)
        
        # Добавляем препараты в список
        for pesticide in sorted_pesticides:
            card = PesticideCard()
            
            # Заполняем данные с проверкой на None
            card.pesticide_name = pesticide.get('name', '')
            card.pesticide_description = pesticide.get('description', '')
            card.pesticide_price = f"{pesticide.get('price', 0)} руб."
            card.pesticide_packaging = pesticide.get('packaging', '')
            card.pesticide_application_rate = pesticide.get('application_rate', '')
            
            # Для тестовых данных формируем строку ДВ
            substances_text = "Действующие вещества:\n"
            if pesticide.get('substance'):
                substances_text += f": {pesticide.get('substance')}\n"
            else:
                substances_text += "Не указаны"
            
            card.pesticide_substance = substances_text.strip()
            
            card.on_release = lambda p=pesticide: self.show_pesticide_details(p)
            
            pesticides_list.add_widget(card)


    # def edit_pesticide(self, pesticide):
    #     """Редактировать препарат"""
    #     self.current_editing_pesticide = pesticide
        
    #     # Создаем диалог редактирования
    #     self.edit_dialog = MDDialog(
    #         title="Редактирование препарата",  # Только здесь заголовок
    #         type="custom",
    #         content_cls=EditPesticideDialog(
    #             pesticide_data=pesticide,
    #             save_callback=self.save_pesticide_changes,
    #             delete_callback=self.delete_pesticide,
    #             cancel_callback=self.cancel_edit,
    #             catalog_instance=self  # Передаем ссылку на каталог
    #         ),
    #         size_hint=(0.9, 0.8),  # 80% высоты окна
    #         auto_dismiss=False
    #     )
    #     self.edit_dialog.open()

    def edit_pesticide(self, pesticide):
        """Редактирование препарата"""
        print(f"✏️ Редактирование препарата: {pesticide['name']}")
        
        # Закрываем детальный диалог если открыт
        if hasattr(self, 'detail_dialog') and self.detail_dialog:
            self.detail_dialog.dismiss()
        
        # Сохраняем препарат для редактирования
        self.current_editing_pesticide = pesticide
        
        # Создаем или обновляем диалог редактирования
        if not hasattr(self, 'edit_dialog') or not self.edit_dialog:
            self._create_edit_dialog()
        
        # Заполняем поля данными препарата
        self._populate_edit_fields(pesticide)
        
        # Открываем диалог
        self.edit_dialog.open()

    def _create_edit_dialog(self):
        """Создание диалога редактирования препарата"""
        # Создаем поля формы (БЕЗ поля "Единица измерения")
        self.name_field = MDTextField(
            hint_text="Название препарата",
            mode="rectangle",
            size_hint_x=1
        )
        
        self.description_field = MDTextField(
            hint_text="Описание",
            mode="rectangle",
            size_hint_x=1,
            multiline=True
        )
        
        self.application_rate_field = MDTextField(
            hint_text="Норма расхода",
            mode="rectangle",
            size_hint_x=1
        )
        
        self.packaging_field = MDTextField(
            hint_text="Фасовка",
            mode="rectangle",
            size_hint_x=1
        )
        
        self.price_field = MDTextField(
            hint_text="Цена",
            mode="rectangle",
            size_hint_x=1,
            input_filter='float'
        )
        
        self.manufacturer_field = MDTextField(
            hint_text="Производитель",
            mode="rectangle",
            size_hint_x=1
        )
        
        # Кнопка для редактирования ДВ
        self.edit_substances_btn = MDRectangleFlatButton(
            text="Редактировать действующие вещества",
            size_hint_x=1,
            on_release=lambda x: self._edit_substances()
        )
        
        # Тип пестицида
        self.type_field = MDTextField(
            hint_text="Тип пестицида",
            mode="rectangle",
            size_hint_x=1
        )
        
        # Создаем контейнер для полей
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(15)
        )
        
        # Добавляем поля в контейнер
        content.add_widget(self.name_field)
        content.add_widget(self.description_field)
        content.add_widget(self.application_rate_field)
        content.add_widget(self.packaging_field)
        content.add_widget(self.price_field)
        content.add_widget(self.manufacturer_field)
        content.add_widget(self.edit_substances_btn)  # Кнопка редактирования ДВ
        content.add_widget(self.type_field)
        
        # Создаем диалог
        self.edit_dialog = MDDialog(
            title="Редактирование препарата",
            type="custom",
            content_cls=content,
            size_hint=(0.9, 0.8),
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda x: self.edit_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Сохранить",
                    on_release=lambda x: self._save_pesticide_edit()
                )
            ]
        )

    def _populate_edit_fields(self, pesticide):
        """Заполнение полей формы данными препарата"""
        self.name_field.text = pesticide.get('name', '')
        self.description_field.text = pesticide.get('description', '')
        self.application_rate_field.text = pesticide.get('application_rate', '')
        self.packaging_field.text = pesticide.get('packaging', '')
        self.price_field.text = str(pesticide.get('price', ''))
        self.manufacturer_field.text = pesticide.get('manufacturer', '')
        
        # Тип пестицида
        pesticide_type = pesticide.get('pesticide_type', pesticide.get('type', ''))
        self.type_field.text = pesticide_type

    def _edit_substances(self):
        """Редактирование действующих веществ"""
        if self.current_editing_pesticide and self.current_editing_pesticide.get('id'):
            # Закрываем диалог редактирования
            if self.edit_dialog:
                self.edit_dialog.dismiss()
            
            # Открываем редактор ДВ
            self.app.show_substance_editor(self.current_editing_pesticide['id'])

    def _save_pesticide_edit(self):
        """Сохранение изменений препарата"""
        try:
            # Получаем данные из полей
            updated_pesticide = {
                'name': self.name_field.text,
                'description': self.description_field.text,
                'application_rate': self.application_rate_field.text,
                'packaging': self.packaging_field.text,
                'price': float(self.price_field.text) if self.price_field.text else 0.0,
                'manufacturer': self.manufacturer_field.text,
                'pesticide_type': self.type_field.text
            }
            
            # Здесь должен быть код сохранения в БД 
            print(f"💾 Сохранены изменения препарата: {updated_pesticide['name']}")
            # Закрываем диалог
            self.edit_dialog.dismiss()            
            # Обновляем отображение в каталоге
            self._load_pesticides()
            
        except Exception as e:
            print(f"❌ Ошибка сохранения препарата: {e}")

    def save_pesticide_changes(self, updated_data):
        """Сохранить изменения препарата"""
        print(f"💾 Сохранены изменения: {updated_data['name']}")
        
        try:
            # Находим препарат в тестовых данных и обновляем его
            for i, pesticide in enumerate(self.test_pesticides):
                if pesticide['id'] == self.current_editing_pesticide['id']:
                    # Форматируем цену
                    if 'price' in updated_data and updated_data['price']:
                        if 'руб' not in str(updated_data['price']):
                            updated_data['price'] = f"{updated_data['price']} руб."
                    
                    # Обновляем все поля препарата
                    self.test_pesticides[i].update(updated_data)
                    break
            
            # Закрываем диалог редактирования
            if self.edit_dialog:
                self.edit_dialog.dismiss()
            
            # Закрываем диалог деталей препарата (если открыт)
            if self.detail_dialog:
                self.detail_dialog.dismiss()
            
            # Обновляем список препаратов
            self._load_pesticides(
                search_query=self.ids.search_input.text,
                filters=self.filters
            )
            
            # Показываем сообщение об успехе
            self._show_success_message(f"Препарат '{updated_data['name']}' обновлен")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            self._show_error_message(f"Ошибка сохранения: {e}")
    
    def delete_pesticide(self, pesticide):
        """Удалить препарат"""
        print(f"🗑️ Удален препарат: {pesticide['name']}")
        self.show_snackbar(f"Препарат '{pesticide['name']}' удален")
        
        if self.edit_dialog:
            self.edit_dialog.dismiss()
        
        # Обновляем список
        self._load_pesticides(
            search_query=self.ids.search_input.text,
            filters=self.filters
        )
    
    def cancel_edit(self):
        """Отменить редактирование"""
        # Закрываем меню если оно открыто
        if hasattr(self, 'edit_dialog') and self.edit_dialog:
            content = self.edit_dialog.content_cls
            if hasattr(content, 'type_menu') and content.type_menu:
                content.type_menu.dismiss()
        
        if self.edit_dialog:
            self.edit_dialog.dismiss()
        self.current_editing_pesticide = None
    
    def add_to_order(self, pesticide):
        """Добавить препарат в заказ"""
        print(f"🛒 Добавлен в заказ: {pesticide['name']}")
        if self.detail_dialog:
            self.detail_dialog.dismiss()
        
        self.show_snackbar(f"Препарат '{pesticide['name']}' добавлен в заказ")
       
    def select_pesticide_type(self, pesticide_type):
        """Выбрать тип пестицида в фильтрах"""
        try:
            if self.filter_dialog:
                content = self.filter_dialog.content_cls
                # Получаем текущие выбранные типы
                current_text = content.ids.type_filter.text
                if current_text:
                    # Если уже есть выбранные типы, добавляем новый через запятую
                    types_list = [t.strip() for t in current_text.split(',')]
                    if pesticide_type not in types_list:
                        types_list.append(pesticide_type)
                        content.ids.type_filter.text = ', '.join(types_list)
                    else:
                        # Если уже выбран, убираем его
                        types_list.remove(pesticide_type)
                        content.ids.type_filter.text = ', '.join(types_list)
                else:
                    content.ids.type_filter.text = pesticide_type
                
                if self.type_menu:
                    self.type_menu.dismiss()
                    self.type_menu = None
        except Exception as e:
            print(f"❌ Ошибка выбора типа в фильтрах: {e}")
   
    def apply_filters(self):
        """Применить фильтры"""
        if self.filter_dialog:
            content = self.filter_dialog.content_cls
            
            # Собираем все фильтры
            self.filters = {
                'type': getattr(self, 'selected_types', []).copy(),
                'cultures': getattr(self, 'selected_cultures', []).copy(),
                'diseases': getattr(self, 'selected_diseases', []).copy(),
                'min_price': content.ids.min_price.text,
                'max_price': content.ids.max_price.text
            }
            
            print(f"✅ Применены фильтры: {self.filters}")
            self._load_pesticides(
                search_query=self.ids.search_input.text,
                filters=self.filters
            )
            self.filter_dialog.dismiss()

    def reset_filters(self):
        """Сбросить фильтры"""
        self.filters = {}
        self.selected_types = []
        self.selected_cultures = []
        self.selected_diseases = []
        
        if self.filter_dialog:
            content = self.filter_dialog.content_cls
            content.ids.type_filter.text = ""
            content.ids.culture_filter.text = ""
            content.ids.disease_filter.text = ""
            content.ids.min_price.text = ""
            content.ids.max_price.text = ""
        
        print("🔄 Все фильтры сброшены")
        self._load_pesticides(search_query=self.ids.search_input.text)
    
    def _get_test_pesticides(self):
        """Получить тестовые данные препаратов"""
        return [
            {
                'id': 1,
                'name': 'Гербицид 1',
                'substance': 'Метсульфурон-метил',
                'description': 'Системный гербицид широкого спектра',
                'application_rate': '0,5 л/га',
                'packaging': 'Канистра 5л',
                'price': '2 500',
                'manufacturer': 'Агрохим',
                'unit': 'л',
                'type': 'Гербициды',
                'cultures': 'Пшеница, Ячмень',
                'diseases': 'Сорняки широколистные'
            },
            {
                'id': 2,
                'name': 'Фунгицид Профи',
                'substance': 'Дифеноконазол',
                'description': 'Защита от мучнистой росы и парши',
                'application_rate': '0,2 кг/га',
                'packaging': 'Пакет 1кг',
                'price': '1 800',
                'manufacturer': 'Защита растений',
                'unit': 'кг',
                'type': 'Фунгициды',
                'cultures': 'Яблоня, Груша',
                'diseases': 'Мучнистая роса, Парша'
            },
            {
                'id': 3,
                'name': 'Инсектицид Макс',
                'substance': 'Имидаклоприд',
                'description': 'Кишечно-контактное действие',
                'application_rate': '0,1 л/га',
                'packaging': 'Флакон 1л',
                'price': '3 200',
                'manufacturer': 'Инсект-контроль',
                'unit': 'л',
                'type': 'Инсектициды',
                'cultures': 'Картофель, Томаты',
                'diseases': 'Колорадский жук, Тля'
            },
            {
                'id': 4,
                'name': 'Агротин ВДГ',
                'substance': 'Метсульфурон-метил',
                'description': 'Мощный гербицид для злаковых',
                'application_rate': '0,05 кг/га',
                'packaging': 'Пакет 0,1кг',
                'price': '1 500',
                'manufacturer': 'Агрохим',
                'unit': 'кг',
                'type': 'Гербициды',
                'cultures': 'Пшеница, Рожь',
                'diseases': 'Овсюг, Пырей'
            },
            {
                'id': 5,
                'name': 'Защита Плюс',
                'substance': 'Дифеноконазол',
                'description': 'Фунгицид для плодовых культур',
                'application_rate': '0,3 л/га',
                'packaging': 'Канистра 10л',
                'price': '4 200',
                'manufacturer': 'Защита растений',
                'unit': 'л',
                'type': 'Фунгициды',
                'cultures': 'Яблоня, Виноград',
                'diseases': 'Парша, Милдью'
            }
        ]

    def _show_success_message(self, message):
        """Показать сообщение об успехе"""
        try:
            from kivymd.uix.snackbar import Snackbar
            snackbar = Snackbar(text=message)
            snackbar.open()
        except Exception as e:
            print(f"💬 {message}")
        
        """Показать сообщение об успехе"""
        print(f"✅ {message}")

    def _show_error_message(self, message):
        """Показать сообщение об ошибке"""
        try:
            from kivymd.uix.snackbar import Snackbar
            snackbar = Snackbar(
                text=message,
                bg_color=(0.8, 0.2, 0.2, 1)  # Красный цвет для ошибок
            )
            snackbar.open()
        except Exception as e:
            print(f"❌ {message}")
```

### app\ui\screens\substance_editor.py
**Размер:** 6688 байт  
```python
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.lang import Builder

from app.ui.widgets.substance_item import SubstanceItem

Builder.load_string('''
<SubstanceEditorPopup>:
    size_hint: (0.9, 0.8)
    title: 'Редактирование действующих веществ'
    title_size: dp(18)
    title_align: 'center'
    
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        
        Label:
            text: 'Действующие вещества препарата'
            size_hint_y: None
            height: dp(30)
            font_size: dp(16)
            bold: True
        
        ScrollView:
            id: scroll_view
            size_hint_y: 0.7
            
            BoxLayout:
                id: substances_container
                orientation: 'vertical'
                size_hint_y: None
                spacing: dp(5)
                padding: [dp(5), dp(5)]
        
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            Button:
                text: '+ Добавить ДВ'
                size_hint_x: 0.5
                on_release: root.add_substance_item()
            
            Button:
                text: 'Обновить список ДВ'
                size_hint_x: 0.5
                on_release: root.update_available_substances()
        
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            padding: [0, dp(10), 0, 0]
            
            Button:
                text: 'Сохранить'
                background_color: 0, 0.7, 0, 1
                size_hint_x: 0.5
                on_release: root.save_changes()
            
            Button:
                text: 'Отмена'
                background_color: 0.8, 0, 0, 1
                size_hint_x: 0.5
                on_release: root.dismiss()
''')

class SubstanceEditorPopup(Popup):
    """Popup для редактирования действующих веществ"""
    
    def __init__(self, app, pesticide_id, on_save_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.pesticide_id = pesticide_id
        self.on_save_callback = on_save_callback
        self.available_substances = []
        self.substance_items = []
        
        self.load_data()
    
    def load_data(self):
        """Загрузка данных"""
        # Загружаем доступные вещества
        self.update_available_substances()
        
        # Загружаем текущие вещества препарата
        current_substances = self.app.db.get_pesticide_substances(self.pesticide_id)
        
        # Очищаем контейнер
        container = self.ids.substances_container
        container.clear_widgets()
        self.substance_items = []
        
        # Добавляем текущие вещества
        for substance in current_substances:
            self.add_substance_item(substance)
        
        # Добавляем пустую строку для нового вещества
        self.add_substance_item()
    
    def update_available_substances(self):
        """Обновление списка доступных веществ"""
        self.available_substances = self.app.db.get_all_active_substances()
    
    def add_substance_item(self, substance_data=None):
        """Добавление новой строки для ДВ"""
        item = SubstanceItem(
            available_substances=self.available_substances,
            size_hint_y=None,
            height=dp(50)
        )
        
        if substance_data:
            item.substance_id = substance_data['id']
            item.substance_name = substance_data['name']
            item.concentration = substance_data['concentration']
            item.update_display_text()
        
        # Привязываем обработчики событий
        item.on_save = self.on_item_save
        item.on_delete = self.on_item_delete
        
        self.ids.substances_container.add_widget(item)
        self.substance_items.append(item)
        
        # Обновляем высоту контейнера
        container = self.ids.substances_container
        container.height = len(self.substance_items) * dp(55)
    
    def on_item_save(self, item):
        """Обработка сохранения строки"""
        # Если строка была пустая и теперь заполнена, добавляем новую пустую
        if item.substance_name and not self.substance_items[-1].substance_name:
            self.add_substance_item()
    
    def on_item_delete(self, item):
        """Обработка удаления строки"""
        if item in self.substance_items:
            self.ids.substances_container.remove_widget(item)
            self.substance_items.remove(item)
            
            # Обновляем высоту контейнера
            container = self.ids.substances_container
            container.height = len(self.substance_items) * dp(55)
            
            # Если удалили последнюю непустую строку, добавляем пустую
            if not self.substance_items or all(not i.substance_name for i in self.substance_items):
                self.add_substance_item()
    
    def save_changes(self):
        """Сохранение всех изменений"""
        substances_to_save = []
        
        for item in self.substance_items:
            if item.substance_id and item.concentration:
                substances_to_save.append({
                    'id': item.substance_id,
                    'name': item.substance_name,
                    'concentration': item.concentration
                })
        
        # Сохраняем в БД
        success = self.app.db.save_pesticide_substances(self.pesticide_id, substances_to_save)
        
        if success:
            # Вызываем callback если есть
            if self.on_save_callback:
                self.on_save_callback()
            
            self.dismiss()
```

### app\ui\widgets\__init__.py
**Размер:** 0 байт  
```python

```

### app\ui\widgets\substance_item.py
**Размер:** 5522 байт  
```python
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.lang import Builder
from kivy.metrics import dp

Builder.load_string('''
<SubstanceItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(50)
    padding: [dp(5), dp(5)]
    spacing: dp(5)
    
    Label:
        id: display_label
        text: root.display_text
        size_hint_x: 0.7
        halign: 'left'
        valign: 'middle'
        text_size: self.width, None
        on_touch_down: root.on_label_touch(self, args) if self.collide_point(*args.pos) else False
        
    BoxLayout:
        id: edit_container
        size_hint_x: 0.7
        orientation: 'horizontal'
        spacing: dp(5)
        opacity: 0 if not root.editing else 1
        disabled: not root.editing
        
        DropDownButton:
            id: substance_dropdown
            text: root.substance_name if root.substance_name else 'Выбрать ДВ'
            size_hint_x: 0.6
            on_release: root.show_substance_dropdown()
            
        TextInput:
            id: concentration_input
            text: root.concentration
            hint_text: 'Концентрация'
            size_hint_x: 0.4
            multiline: False
            on_text_validate: root.save_changes()
    
    BoxLayout:
        size_hint_x: 0.3
        orientation: 'horizontal'
        spacing: dp(5)
        
        IconButton:
            id: edit_btn
            icon: 'pencil' if not root.editing else 'content-save'
            size_hint_x: 0.5
            on_release: root.toggle_edit_mode()
            
        IconButton:
            id: delete_btn
            icon: 'delete'
            size_hint_x: 0.5
            on_release: root.delete_item()
''')

class DropDownButton(Button):
    pass

class IconButton(Button):
    pass

class SubstanceItem(BoxLayout):
    """Виджет строки с действующим веществом для inline-редактирования"""
    
    # Свойства
    substance_id = StringProperty('')
    substance_name = StringProperty('')
    concentration = StringProperty('')
    editing = BooleanProperty(False)
    on_save = ObjectProperty(None)
    on_delete = ObjectProperty(None)
    available_substances = ObjectProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown = None
        self.update_display_text()
    
    @property
    def display_text(self):
        """Текст для отображения в режиме просмотра"""
        if self.substance_name and self.concentration:
            return f"{self.substance_name}: {self.concentration}"
        elif self.substance_name:
            return self.substance_name
        return "Не указано"
    
    def update_display_text(self):
        """Обновить текст отображения"""
        self.ids.display_label.text = self.display_text
    
    def on_label_touch(self, instance, touch):
        """Обработка касания метки для перехода в режим редактирования"""
        if touch.is_double_tap and not self.editing:
            self.editing = True
            return True
    
    def toggle_edit_mode(self):
        """Переключение режима редактирования"""
        if self.editing:
            self.save_changes()
        else:
            self.editing = True
    
    def save_changes(self):
        """Сохранение изменений"""
        if self.editing:
            # Обновляем концентрацию
            self.concentration = self.ids.concentration_input.text
            
            # Если выбранное вещество из dropdown
            if hasattr(self, 'selected_substance'):
                self.substance_name = self.selected_substance['name']
                self.substance_id = self.selected_substance['id']
            
            self.update_display_text()
            self.editing = False
            
            if self.on_save:
                self.on_save(self)
    
    def show_substance_dropdown(self):
        """Показать dropdown с доступными веществами"""
        if not self.available_substances:
            return
        
        self.dropdown = DropDown()
        
        for substance in self.available_substances:
            btn = Button(
                text=substance['name'],
                size_hint_y=None,
                height=dp(40)
            )
            btn.bind(on_release=lambda btn, s=substance: self.select_substance(s))
            self.dropdown.add_widget(btn)
        
        self.dropdown.open(self.ids.substance_dropdown)
    
    def select_substance(self, substance):
        """Выбор вещества из dropdown"""
        self.selected_substance = substance
        self.ids.substance_dropdown.text = substance['name']
        if self.dropdown:
            self.dropdown.dismiss()
    
    def delete_item(self):
        """Удаление строки"""
        if self.on_delete:
            self.on_delete(self)
```

### export_project_v1.py
**Размер:** 10701 байт  
```python
import os
import pathlib
from datetime import datetime

def export_project(root_path=".", output_file="project_export.md"):
    """
    Экспортирует структуру и код проекта в один Markdown файл.
    """
    
    # Директории для исключения
    exclude_dirs = {
        '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
        'venv', '.venv', 'env', '.env', 'envs',
        '.vscode', '.idea', 'vs_code',
        'dist', 'build', '*.egg-info',
        'node_modules', 'coverage', '.coverage',
        '.github', '.gitlab', '.bitbucket',
        'poetry_env', 'virtual_env'  # добавил специфичные для poetry
    }
    
    # Файлы для исключения
    exclude_files = {
        '*.pyc', '*.pyo', '*.pyd', '*.so',
        '*.db', '*.sqlite', '*.sqlite3', '*.log',
        'poetry.lock', 'package-lock.json', 'yarn.lock',
        '.gitignore', '.env', '.env.local', '.env.*',
        'Thumbs.db', 'desktop.ini'
    }
    
    root_path = pathlib.Path(root_path).resolve()
    
    with open(output_file, 'w', encoding='utf-8') as out:
        # Заголовок
        out.write(f"# Экспорт проекта: {root_path.name}\n")
        out.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"**Путь:** {root_path}\n\n")
        
        # Структура проекта
        out.write("## Структура проекта\n\n")
        out.write("```\n")
        
        # Сначала собираем структуру
        structure_lines = []
        
        for root, dirs, files in os.walk(root_path):
            # Фильтруем директории
            dirs[:] = [
                d for d in dirs 
                if d not in exclude_dirs 
                and not d.startswith('.')
                and not d.endswith('__pycache__')
            ]
            
            # Относительный путь
            try:
                rel_root = pathlib.Path(root).relative_to(root_path)
            except ValueError:
                continue
            
            # Определяем отступ
            if str(rel_root) == '.':
                indent_level = 0
            else:
                indent_level = len(rel_root.parts)
            
            indent = "  " * indent_level
            
            if str(rel_root) != '.':
                structure_lines.append(f"{indent}{rel_root.name}/")
            
            # Файлы
            for file in sorted(files):
                if any(file.endswith(ext.strip('*')) for ext in exclude_files if '*' in ext):
                    continue
                if file in exclude_files:
                    continue
                if any(file == pattern for pattern in exclude_files):
                    continue
                    
                structure_lines.append(f"{indent}  {file}")
        
        # Записываем структуру
        for line in structure_lines:
            out.write(f"{line}\n")
        
        out.write("```\n\n")
        
        # Содержимое файлов
        out.write("## Содержимое файлов\n\n")
        
        file_count = 0
        total_size = 0
        excluded_count = 0
        
        for root, dirs, files in os.walk(root_path):
            # Фильтруем директории
            dirs[:] = [
                d for d in dirs 
                if d not in exclude_dirs 
                and not d.startswith('.')
                and not d.endswith('__pycache__')
            ]
            
            for file in sorted(files):
                file_path = pathlib.Path(root) / file
                
                # Проверяем исключения для файлов
                skip = False
                
                # Проверка по расширению (шаблоны типа *.pyc)
                for pattern in exclude_files:
                    if pattern.startswith('*'):
                        ext = pattern[1:]  # убираем звездочку
                        if file.endswith(ext):
                            excluded_count += 1
                            skip = True
                            break
                    elif file == pattern:
                        excluded_count += 1
                        skip = True
                        break
                
                if skip:
                    continue
                
                # Дополнительные проверки
                if file.startswith('.'):
                    excluded_count += 1
                    continue
                
                try:
                    rel_path = file_path.relative_to(root_path)
                except ValueError:
                    continue
                
                # Определяем язык для подсветки синтаксиса
                ext = file_path.suffix.lower()
                lang_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript',
                    '.html': 'html',
                    '.css': 'css',
                    '.md': 'markdown',
                    '.json': 'json',
                    '.yml': 'yaml',
                    '.yaml': 'yaml',
                    '.txt': 'text',
                    '.toml': 'toml',
                    '.ini': 'ini',
                    '.xml': 'xml',
                    '.csv': 'csv',
                    '.sql': 'sql',
                }
                lang = lang_map.get(ext, '')
                
                out.write(f"### 📄 {rel_path}\n")
                out.write(f"**Размер:** {file_path.stat().st_size} байт  \n")
                
                try:
                    # Читаем файл с обработкой разных кодировок
                    try:
                        content = file_path.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            content = file_path.read_text(encoding='cp1251')
                        except:
                            content = f"# Не удалось прочитать файл (бинарный или неизвестная кодировка)\n"
                    
                    # Обрезаем слишком большие файлы
                    max_lines = 1000
                    lines = content.split('\n')
                    if len(lines) > max_lines:
                        content = '\n'.join(lines[:max_lines])
                        content += f"\n\n# ... файл обрезан, показано {max_lines} из {len(lines)} строк ..."
                    
                    out.write(f"```{lang}\n")
                    out.write(content)
                    if not content.endswith('\n'):
                        out.write('\n')
                    out.write("```\n\n")
                    
                    file_count += 1
                    total_size += file_path.stat().st_size
                    
                except Exception as e:
                    out.write(f"```\n# Ошибка при чтении файла: {e}\n```\n\n")
        
        # Статистика
        out.write("## Статистика\n\n")
        out.write(f"- **Экспортировано файлов:** {file_count}\n")
        out.write(f"- **Исключено файлов:** {excluded_count}\n")
        out.write(f"- **Общий размер:** {total_size} байт ({total_size/1024:.2f} KB)\n")
        out.write(f"- **Дата экспорта:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    print("🔍 Поиск корня Poetry проекта...")
    current_dir = pathlib.Path.cwd()
    
    # Ищем pyproject.toml в текущей или родительской директории
    project_root = None
    
    # Проверяем текущую директорию
    if (current_dir / "pyproject.toml").exists():
        project_root = current_dir
        print(f"✅ Найден Poetry проект в текущей папке: {project_root}")
    
    # Если не нашли, проверяем родительскую
    elif (current_dir.parent / "pyproject.toml").exists():
        project_root = current_dir.parent
        print(f"⚠️  Pyproject.toml найден в родительской папке: {project_root}")
        print(f"   Текущая папка: {current_dir.name}")
        choice = input("   Экспортировать из родительской папки? (y/n): ")
        if choice.lower() != 'y':
            project_root = current_dir
    
    # Если pyproject.toml не найден, используем текущую директорию
    if project_root is None:
        project_root = current_dir
        print(f"⚠️  Pyproject.toml не найден, экспортирую текущую папку: {project_root}")
    
    # Создаем имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"PROJECT_EXPORT_{timestamp}.md"
    
    print(f"📂 Экспорт из: {project_root}")
    print(f"📄 Выходной файл: {output_filename}")
    print("⏳ Выполняется экспорт...")
    
    try:
        export_project(project_root, output_filename)
        print(f"✅ Экспорт успешно завершен!")
        print(f"📊 Файл сохранен как: {output_filename}")
        print("\n📋 Что делать дальше:")
        print(f"   1. Откройте файл в VS Code: code {output_filename}")
        print(f"   2. Или просмотрите в любом Markdown-редакторе")
        print(f"   3. Файл содержит полную структуру и код проекта")
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
        print("🔄 Попробуйте запустить скрипт из корневой папки проекта:")
        print(f"   cd {project_root}")
        print("   python export_project_v2.py")
```

### main.py
**Размер:** 3059 байт  
```python
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window 
from kivy.metrics import dp

from app.core.config import AppConfig
from app.core.database import DatabaseManager
from app.ui.screens.main_screen import MainScreen

class PlantProtectionApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = AppConfig()
        self.db = DatabaseManager()
        self.screen_manager = None

    def build(self):
        Window.size = (dp(390), dp(640))
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        
        # Инициализация компонентов
        self._initialize_components()
        
        # Создание интерфейса
        return self._create_interface()

    def _initialize_components(self):
        """Инициализация основных компонентов приложения"""
        try:
            # Инициализация базы данных
            self.db.initialize()
            print("✅ База данных инициализирована")
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")

    def _create_interface(self):
        """Создание интерфейса приложения"""
        self.screen_manager = ScreenManager()
        
        # Добавляем главный экран
        main_screen = MainScreen(name='main')
        self.screen_manager.add_widget(main_screen)
        
        return self.screen_manager
    
    def show_substance_editor(self, pesticide_id):
        """Показать редактор действующих веществ"""
        from app.ui.screens.substance_editor import SubstanceEditorPopup
        
        def refresh_catalog():
            # Обновить отображение в каталоге
            current_screen = self.screen_manager.current_screen
            if hasattr(current_screen, 'refresh_pesticide'):
                current_screen.refresh_pesticide(pesticide_id)
        
        popup = SubstanceEditorPopup(
            app=self,
            pesticide_id=pesticide_id,
            on_save_callback=refresh_catalog
        )
        popup.open()

    # Методы навигации
    def open_diagnosis(self):
        print("📷 Открыть диагностику заболеваний")
    
    def open_catalog(self):
        print("📚 Открыть каталог препаратов")
    
    def open_orders(self):
        print("🛒 Открыть заказы и клиенты")
    
    def open_settings(self):
        print("⚙️ Открыть настройки")
    
    def navigation_draw(self):
        print("📋 Открыть меню навигации")

if __name__ == '__main__':
    PlantProtectionApp().run()
```

### main_db_test.py
**Размер:** 6825 байт  
```python
"""
ТЕСТ БАЗЫ ДАННЫХ - РАБОЧАЯ ВЕРСИЯ
Эту версию можно использовать для проверки БД в любой момент
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from pathlib import Path

from app.core.database_backup import DatabaseManagerBackup as DatabaseManager

class DatabaseTestApp(App):
    """
    Тестовое приложение для проверки работы базы данных
    Сохраните этот файл как резервную копию рабочей конфигурации
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()  # Теперь использует тестовую версию
        self.status_label = None
    
    def build(self):
        # Главный layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Заголовок
        title = Label(
            text='Plant Protection App - Тест БД',
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # Статус
        self.status_label = Label(
            text='Нажмите для инициализации БД',
            font_size='16sp',
            size_hint_y=None,
            height=100,
            text_size=(400, None)
        )
        layout.add_widget(self.status_label)
        
        # Кнопки
        btn_init = Button(
            text='1. Инициализировать БД',
            size_hint_y=None,
            height=50,
            on_press=self.initialize_database
        )
        layout.add_widget(btn_init)
        
        btn_check = Button(
            text='2. Проверить файл БД',
            size_hint_y=None,
            height=50,
            on_press=self.check_database_file
        )
        layout.add_widget(btn_check)
        
        btn_show = Button(
            text='3. Показать классы заболеваний',
            size_hint_y=None,
            height=50,
            on_press=self.show_disease_classes
        )
        layout.add_widget(btn_show)
        
        btn_search = Button(
            text='4. Тест поиска препаратов',
            size_hint_y=None,
            height=50,
            on_press=self.test_search
        )
        layout.add_widget(btn_search)
        
        btn_tables = Button(
            text='5. Показать все таблицы',
            size_hint_y=None,
            height=50,
            on_press=self.show_tables_info
        )
        layout.add_widget(btn_tables)
        
        return layout
    
    def show_message(self, message):
        """Показать сообщение в статусе"""
        if self.status_label:
            self.status_label.text = message
        print("💬", message)
    
    def check_database_file(self, instance=None):
        """Проверить существование файла БД"""
        try:
            db_path = Path(__file__).parent / "app" / "assets" / "database" / "plant_protection.db"
            exists = db_path.exists()
            size = db_path.stat().st_size if exists else 0
            
            if exists:
                self.show_message(f"✅ Файл БД существует\nРазмер: {size} байт\nПуть: {db_path}")
            else:
                self.show_message("❌ Файл БД не найден")
        except Exception as e:
            self.show_message(f"❌ Ошибка проверки: {e}")
    
    def initialize_database(self, instance=None):
        """Инициализация базы данных"""
        try:
            success = self.db.initialize()
            if success:
                self.show_message("✅ БД успешно инициализирована!")
                self.check_database_file()
            else:
                self.show_message("❌ Ошибка инициализации БД")
        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            self.show_message(error_msg)
    
    def show_disease_classes(self, instance=None):
        """Показать классы заболеваний"""
        try:
            classes = self.db.get_all_disease_classes()
            if classes:
                class_names = "\n".join([f"{cls[1]}: {cls[2]}" for cls in classes])
                self.show_message(f"Классы заболеваний:\n{class_names}")
            else:
                self.show_message("Классы заболеваний не найдены")
        except Exception as e:
            self.show_message(f"Ошибка: {e}")
    
    def test_search(self, instance=None):
        """Тест поиска препаратов"""
        try:
            results = self.db.search_pesticides("Агротин")
            if results:
                pesticide_names = "\n".join([f"{pest[1]} - {pest[5]} руб." for pest in results])
                self.show_message(f"Найдены препараты:\n{pesticide_names}")
            else:
                self.show_message("Препараты не найдены")
        except Exception as e:
            self.show_message(f"Ошибка поиска: {e}")
    
    def show_tables_info(self, instance=None):
        """Показать информацию о всех таблицах"""
        try:
            cursor = self.db.connection.cursor()
            
            # Получаем список всех таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            table_info = []
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_info.append(f"{table_name}: {count} записей")
            
            self.show_message("Таблицы в БД:\n" + "\n".join(table_info))
            
        except Exception as e:
            self.show_message(f"Ошибка получения таблиц: {e}")

if __name__ == '__main__':
    print("🚀 Запуск теста базы данных...")
    print("💾 Эта версия сохранена как резервная копия")
    DatabaseTestApp().run()
```

### migrate_db.py
**Размер:** 15459 байт  
```python
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
```

### pyproject.toml
**Размер:** 731 байт  
```toml
[tool.poetry]
name = "plant-protection-app"
version = "0.1.0"
description = "My test version of mobile_plant_app"
authors = ["nell.fdorova.00@mail.ru"]
readme = ""  # УБРАТЬ README.md
packages = [{include = "app"}]

# Добавьте эту строку чтобы отключить package mode:
package-mode = false

[tool.poetry.dependencies]
python = "^3.11"
kivy = "^2.3.0"
kivymd = "^1.1.1"
pillow = "^10.0.0"
opencv-python = "^4.8.0"
numpy = ">=1.24,<2"
pandas = "^2.0.0"
openpyxl = "^3.1.0"
sqlalchemy = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"
flake8 = "^6.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry-core.metadata"
```

### smart_export_full.py
**Размер:** 32357 байт  
```python
import os
import ast
import pathlib
import argparse
from datetime import datetime
from typing import Set, List, Dict, Optional
import re
import sqlite3
import json

class SmartProjectExporter:
    """
    Умный экспорт проекта с зависимостями.
    Экспортирует структуру, целевой файл и все его зависимости.
    Включает полное содержимое файлов и структуру базы данных.
    """
    
    def __init__(self, root_path="."):
        self.root_path = pathlib.Path(root_path).resolve()
        
        # Директории для исключения
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
            'venv', '.venv', 'env', '.env', 'envs',
            '.vscode', '.idea', 'vs_code',
            'dist', 'build', '*.egg-info',
            'node_modules', 'coverage', '.coverage',
            '.github', '.gitlab', '.bitbucket',
            'generated_docs'
        }
        
        # Файлы для исключения
        self.exclude_files = {
            '*.pyc', '*.pyo', '*.pyd', '*.so',
            '*.log',
            'poetry.lock', 'package-lock.json', 'yarn.lock',
            '.gitignore', '.env', '.env.local', '.env.*',
            'Thumbs.db', 'desktop.ini', '.DS_Store',
            'advanced_documentation.py'  # Исключаем файл генерации документации
        }
        
        # Полные пути для исключения (относительно корня проекта)
        self.exclude_full_paths = {
            'advanced_documentation.py',  # Файл в корне проекта
        }
        
        self.import_graph: Dict[str, Set[str]] = {}
        self.analyzed_files: Set[str] = set()
        
    def should_skip(self, path: pathlib.Path) -> bool:
        """Определить, нужно ли пропустить файл/папку"""
        name = path.name
        
        # Пропускаем скрытые файлы
        if name.startswith('.'):
            return True
        
        # Пропускаем исключенные директории
        if path.is_dir():
            for pattern in self.exclude_dirs:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern:
                    return True
        
        # Пропускаем файлы в исключенных директориях
        for parent in path.parents:
            if parent.name in self.exclude_dirs:
                return True
        
        # Проверяем полный путь файла относительно корня проекта
        try:
            rel_path = str(path.relative_to(self.root_path))
            if rel_path in self.exclude_full_paths:
                return True
        except ValueError:
            pass
        
        # Пропускаем исключенные файлы по шаблону
        if path.is_file():
            for pattern in self.exclude_files:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern:
                    return True
        
        return False
    
    def analyze_imports(self, file_path: pathlib.Path) -> Set[str]:
        """Анализирует импорты в файле и возвращает зависимости"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Стандартные импорты
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
                    elif node.level > 0:
                        current_dir = file_path.parent
                        for i in range(node.level - 1):
                            current_dir = current_dir.parent
                        for name_obj in node.names:
                            possible_names = [
                                f"{name_obj.name}.py",
                                f"{name_obj.name}/__init__.py"
                            ]
                            for possible in possible_names:
                                possible_path = current_dir / possible
                                if possible_path.exists():
                                    rel_path = possible_path.relative_to(self.root_path)
                                    imports.add(str(rel_path).replace('.py', '').replace('/', '.'))
            
            # Анализ строковых импортов
            string_imports = re.findall(r"from\s+['\"](.+?)['\"]", content)
            string_imports += re.findall(r"import\s+['\"](.+?)['\"]", content)
            
            for imp in string_imports:
                imports.add(imp.split('.')[0])
                
        except Exception as e:
            print(f"Ошибка анализа {file_path}: {e}")
        
        return imports
    
    def find_dependencies(self, target_file: pathlib.Path) -> Set[pathlib.Path]:
        """Находит все зависимости для целевого файла"""
        all_deps = set()
        to_analyze = {target_file}
        
        print(f"Поиск зависимостей для {target_file.name}...")
        
        while to_analyze:
            current_file = to_analyze.pop()
            
            if current_file in self.analyzed_files:
                continue
                
            self.analyzed_files.add(current_file)
            
            if not current_file.exists():
                print(f"Файл не найден: {current_file}")
                continue
            
            imports = self.analyze_imports(current_file)
            self.import_graph[str(current_file.relative_to(self.root_path))] = imports
            
            for imp in imports:
                found_files = self.find_file_by_import(imp, current_file.parent)
                for found_file in found_files:
                    if found_file not in self.analyzed_files:
                        to_analyze.add(found_file)
                        all_deps.add(found_file)
            
            self._add_special_dependencies(current_file, all_deps, to_analyze)
        
        return all_deps
    
    def find_file_by_import(self, import_name: str, search_from: pathlib.Path) -> List[pathlib.Path]:
        """Находит файл по имени импорта"""
        found_files = []
        
        possible_paths = [
            self.root_path / import_name.replace('.', '/') / '__init__.py',
            self.root_path / f"{import_name.replace('.', '/')}.py",
            search_from / f"{import_name}.py",
            search_from / import_name / '__init__.py',
            self.root_path / 'app' / import_name.replace('.', '/') / '__init__.py',
            self.root_path / 'app' / f"{import_name.replace('.', '/')}.py",
        ]
        
        for pattern in [f"**/{import_name}.py", f"**/{import_name}/__init__.py"]:
            try:
                for found in self.root_path.glob(pattern):
                    if not self.should_skip(found):
                        found_files.append(found)
            except Exception:
                pass
        
        unique_files = []
        for file in found_files:
            if file.exists() and file not in unique_files:
                unique_files.append(file)
        
        return unique_files
    
    def _add_special_dependencies(self, current_file: pathlib.Path, 
                                  all_deps: Set[pathlib.Path], 
                                  to_analyze: Set[pathlib.Path]):
        """Добавляет специальные зависимости на основе содержимого файла"""
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            current_rel = str(current_file.relative_to(self.root_path))
            
            if 'database' in current_file.name.lower() or 'db' in current_file.name.lower():
                for pattern in ['**/config.py', '**/configs.py', '**/settings.py', '**/models.py', '**/schema.py']:
                    for config_file in self.root_path.glob(pattern):
                        if not self.should_skip(config_file) and config_file not in all_deps:
                            all_deps.add(config_file)
                            to_analyze.add(config_file)
            
            if any(x in current_rel for x in ['screen', 'widget', 'ui']):
                for pattern in ['**/widgets/**/*.py', '**/ui/**/*.py']:
                    for ui_file in self.root_path.glob(pattern):
                        if not self.should_skip(ui_file) and ui_file != current_file:
                            try:
                                with open(ui_file, 'r', encoding='utf-8') as f_ui:
                                    ui_content = f_ui.read()
                                ui_name = ui_file.stem
                                if ui_name in content or ui_name in current_rel:
                                    all_deps.add(ui_file)
                            except:
                                pass
                
                main_files = ['main.py', 'app.py', '__main__.py']
                for main_file in main_files:
                    main_path = self.root_path / main_file
                    if main_path.exists() and main_path not in all_deps:
                        all_deps.add(main_path)
            
            if 'config' in current_file.name.lower():
                for env_file in self.root_path.glob('**/.env*'):
                    if not self.should_skip(env_file):
                        all_deps.add(env_file)
        
        except Exception as e:
            print(f"Ошибка при анализе специальных зависимостей {current_file}: {e}")
    
    def _get_database_structure(self) -> str:
        """Получает структуру базы данных (без данных)"""
        db_structure = "## Структура базы данных\n\n"
        
        db_extensions = ['.db', '.sqlite', '.sqlite3']
        db_files = []
        
        for ext in db_extensions:
            for db_file in self.root_path.glob(f"**/*{ext}"):
                if not self.should_skip(db_file):
                    db_files.append(db_file)
        
        if not db_files:
            db_structure += "Файлы базы данных не найдены.\n\n"
            return db_structure
        
        for db_file in db_files:
            db_structure += f"### База данных: `{db_file.relative_to(self.root_path)}`\n\n"
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
                tables = cursor.fetchall()
                
                if not tables:
                    db_structure += "Таблицы не найдены.\n\n"
                    continue
                
                db_structure += "**Таблицы:**\n\n"
                
                for table in tables:
                    table_name = table[0]
                    if table_name == 'sqlite_sequence':
                        continue
                    
                    db_structure += f"#### Таблица: `{table_name}`\n\n"
                    
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    
                    db_structure += "| Колонка | Тип | Nullable | Default | PK |\n"
                    db_structure += "|---------|-----|----------|---------|----|\n"
                    
                    for col in columns:
                        col_id, col_name, col_type, not_null, default_val, pk = col
                        nullable = "Нет" if not_null else "Да"
                        is_pk = "Да" if pk else "Нет"
                        default_val = default_val if default_val else "NULL"
                        db_structure += f"| `{col_name}` | `{col_type}` | {nullable} | `{default_val}` | {is_pk} |\n"
                    
                    db_structure += "\n"
                    
                    cursor.execute(f"PRAGMA index_list({table_name});")
                    indexes = cursor.fetchall()
                    
                    if indexes:
                        db_structure += "**Индексы:**\n\n"
                        for idx in indexes:
                            idx_id, idx_name, unique = idx
                            cursor.execute(f"PRAGMA index_info({idx_name});")
                            idx_cols = cursor.fetchall()
                            col_names = [col[2] for col in idx_cols]
                            unique_str = "Уникальный" if unique else "Неуникальный"
                            db_structure += f"- `{idx_name}` ({unique_str}): {', '.join(col_names)}\n"
                        db_structure += "\n"
                    
                    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                    fks = cursor.fetchall()
                    
                    if fks:
                        db_structure += "**Внешние ключи:**\n\n"
                        for fk in fks:
                            id_, seq, table_from, table_to, col_from, col_to, on_update, on_delete, match = fk
                            db_structure += f"- `{col_from}` → `{table_to}.{col_to}` "
                            db_structure += f"(ON UPDATE: {on_update}, ON DELETE: {on_delete})\n"
                        db_structure += "\n"
                
                conn.close()
                
            except Exception as e:
                db_structure += f"Ошибка при чтении базы данных: {e}\n\n"
        
        return db_structure
    
    def _find_database_related_files(self) -> Set[pathlib.Path]:
        """Находит файлы, связанные с работой с базой данных"""
        db_files = set()
        
        keywords = ['database', 'db', 'model', 'schema', 'table', 'migration']
        
        for pattern in ['**/*.py', '**/*.pyi']:
            for file_path in self.root_path.glob(pattern):
                if self.should_skip(file_path):
                    continue
                
                file_name_lower = file_path.name.lower()
                if any(keyword in file_name_lower for keyword in keywords):
                    db_files.add(file_path)
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    db_indicators = [
                        'sqlalchemy', 'create table', 'create database',
                        'foreign key', 'primary key', 'db.session',
                        'db.execute', 'cursor.execute', 'sqlite3',
                        'orm', 'declarative_base', 'db.Model'
                    ]
                    
                    if any(indicator in content for indicator in db_indicators):
                        db_files.add(file_path)
                        
                except:
                    pass
        
        return db_files
    
    def export_smart(self, target_file: str, output_file: Optional[str] = None):
        """
        Умный экспорт: целевой файл + все его зависимости + структура БД
        
        Args:
            target_file: Путь к целевому файлу
            output_file: Имя выходного файла
        """
        target_path = self.root_path / target_file
        if not target_path.exists():
            found_files = list(self.root_path.glob(f"**/{target_file}"))
            if not found_files:
                raise FileNotFoundError(f"Файл {target_file} не найден в проекте")
            target_path = found_files[0]
            print(f"Найден файл: {target_path.relative_to(self.root_path)}")
        
        all_deps = self.find_dependencies(target_path)
        
        files_to_export = {target_path}
        files_to_export.update(all_deps)
        
        db_related_files = self._find_database_related_files()
        files_to_export.update(db_related_files)
        
        main_files = [
            self.root_path / 'main.py',
            self.root_path / 'pyproject.toml',
            self.root_path / 'requirements.txt',
        ]
        
        for main_file in main_files:
            if main_file.exists():
                files_to_export.add(main_file)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_name = target_path.stem
            output_file = f"SMART_EXPORT_{target_name}_{timestamp}.md"
        
        self._write_export(files_to_export, target_path, output_file)
        
        return output_file, len(files_to_export)
    
    def _write_export(self, files: Set[pathlib.Path], 
                     target_file: pathlib.Path,
                     output_file: str):
        """Записывает экспорт в файл"""
        
        sorted_files = sorted(files, key=lambda x: str(x.relative_to(self.root_path)))
        
        with open(output_file, 'w', encoding='utf-8') as out:
            target_rel = target_file.relative_to(self.root_path)
            out.write(f"# Умный экспорт: {target_rel}\n")
            out.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"**Целевой файл:** `{target_rel}`\n")
            out.write(f"**Проект:** {self.root_path.name}\n\n")
            
            out.write("## Обзор зависимостей\n\n")
            
            out.write("```\n")
            out.write(f"Целевой файл: {target_rel}\n")
            out.write("Зависимости:\n")
            
            for file in sorted_files:
                if file == target_file:
                    continue
                rel_path = file.relative_to(self.root_path)
                out.write(f"  ├── {rel_path}\n")
            out.write("```\n\n")
            
            out.write("## Структура экспорта\n\n")
            out.write("```\n")
            
            dir_structure = {}
            for file in sorted_files:
                rel_path = file.relative_to(self.root_path)
                parent = str(rel_path.parent)
                if parent == '.':
                    parent = ''
                if parent not in dir_structure:
                    dir_structure[parent] = []
                dir_structure[parent].append(rel_path.name)
            
            def print_dir(dir_path: str, indent: int = 0):
                if dir_path in dir_structure:
                    prefix = "  " * indent
                    if dir_path:
                        out.write(f"{prefix}{dir_path.split('/')[-1]}/\n")
                    for file in sorted(dir_structure[dir_path]):
                        file_prefix = "  " * (indent + 1)
                        icon = ">>>" if dir_path == str(target_file.parent) and file == target_file.name else "   "
                        out.write(f"{file_prefix}{icon} {file}\n")
                
                subdirs = []
                if dir_path:
                    dir_prefix = dir_path + '/'
                    subdirs = [
                        d for d in dir_structure.keys()
                        if d.startswith(dir_prefix) and dir_prefix.count('/') == d.count('/') - 1
                    ]
                else:
                    subdirs = [
                        d for d in dir_structure.keys()
                        if d and '/' not in d
                    ]
                
                for subdir in sorted(set(subdirs)):
                    print_dir(subdir, indent + 1)
                    
            out.write("```\n\n")
            
            db_structure = self._get_database_structure()
            out.write(db_structure)
            
            out.write("## Содержимое файлов\n\n")
            
            total_size = 0
            file_count = 0
            
            for i, file in enumerate(sorted_files, 1):
                rel_path = file.relative_to(self.root_path)
                
                ext = file.suffix.lower()
                lang_map = {
                    '.py': 'python',
                    '.toml': 'toml',
                    '.txt': 'text',
                    '.ini': 'ini',
                    '.cfg': 'ini',
                    '.md': 'markdown',
                    '.json': 'json',
                    '.yml': 'yaml',
                    '.yaml': 'yaml',
                }
                lang = lang_map.get(ext, '')
                
                out.write(f"### {rel_path}\n")
                
                if file == target_file:
                    out.write("**ЦЕЛЕВОЙ ФАЙЛ**  \n")
                
                try:
                    file_size = file.stat().st_size
                    out.write(f"**Размер:** {file_size} байт  \n")
                    total_size += file_size
                    file_count += 1
                    
                    if str(rel_path) in self.import_graph:
                        imports = self.import_graph[str(rel_path)]
                        if imports:
                            out.write(f"**Импортирует:** `{', '.join(sorted(imports))}`  \n")
                    
                except Exception as e:
                    out.write(f"**Ошибка:** {e}  \n")
                
                try:
                    try:
                        content = file.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            content = file.read_text(encoding='cp1251')
                        except:
                            content = f"Файл в бинарном формате или неизвестной кодировке\n"
                    
                    out.write(f"```{lang}\n")
                    out.write(content)
                    if not content.endswith('\n'):
                        out.write('\n')
                    out.write("```\n\n")
                    
                except Exception as e:
                    out.write(f"```\nОшибка при чтении файла: {e}\n```\n\n")
            
            out.write("## Статистика экспорта\n\n")
            out.write(f"- **Всего файлов:** {file_count}\n")
            out.write(f"- **Целевой файл:** `{target_rel}`\n")
            out.write(f"- **Зависимостей найдено:** {len(files) - 1}\n")
            out.write(f"- **Общий размер:** {total_size} байт ({total_size/1024:.1f} KB)\n")
            out.write(f"- **Глубина анализа:** {len(self.analyzed_files)} файлов проанализировано\n")
            
            out.write("\n## Рекомендации по использованию\n\n")
            out.write("1. **Целевой файл** помечен значком >>>\n")
            out.write("2. Порядок файлов соответствует структуре проекта\n")
            out.write("3. **Исключены из экспорта:**\n")
            out.write("   - Файл advanced_documentation.py (генерация документации)\n")
            out.write("   - Служебные файлы и директории\n")
            out.write("4. Зависимости включают:\n")
            out.write("   - Прямые импорты (import/from)\n")
            out.write("   - Родственные модули\n")
            out.write("   - Конфигурационные файлы\n")
            out.write("   - Основные файлы проекта (main.py и др.)\n")
            out.write("5. **Структура базы данных** включает:\n")
            out.write("   - Все таблицы и их колонки\n")
            out.write("   - Индексы и внешние ключи\n")
            out.write("   - Файлы моделей и схем\n")
            out.write("\n## Граф зависимостей (текстовый)\n\n")
            out.write("```\n")
            self._write_dependency_graph(out, target_file)
            out.write("```\n")

    def _write_dependency_graph(self, out, target_file: pathlib.Path):
        """Записывает текстовый граф зависимостей"""
        target_rel = str(target_file.relative_to(self.root_path))
        
        graph = {}
        for file, imports in self.import_graph.items():
            for imp in imports:
                possible_files = []
                for dep_file in self.analyzed_files:
                    dep_rel = str(dep_file.relative_to(self.root_path))
                    if imp in dep_rel.replace('/', '.').replace('.py', ''):
                        possible_files.append(dep_rel)
                
                if possible_files:
                    if file not in graph:
                        graph[file] = []
                    graph[file].extend(possible_files)
        
        out.write(f"{target_rel}\n")
        visited = set()
        
        def print_node(node: str, indent: int = 0):
            if node in visited:
                out.write("  " * indent + f"└── {node} (циклическая ссылка)\n")
                return
                
            visited.add(node)
            
            if node in graph:
                deps = graph[node]
                for i, dep in enumerate(sorted(deps)):
                    prefix = "  " * indent
                    if i == len(deps) - 1:
                        out.write(f"{prefix}└── {dep}\n")
                        print_node(dep, indent + 1)
                    else:
                        out.write(f"{prefix}├── {dep}\n")
                        print_node(dep, indent + 1)
        
        print_node(target_rel)


def find_pyproject_root() -> pathlib.Path:
    """Находит корень проекта по pyproject.toml"""
    current_dir = pathlib.Path.cwd()
    
    if (current_dir / "pyproject.toml").exists():
        return current_dir
    
    elif (current_dir.parent / "pyproject.toml").exists():
        print(f"Pyproject.toml найден в родительской папке: {current_dir.parent}")
        choice = input("   Использовать родительскую папку как корень проекта? (y/n): ")
        if choice.lower() == 'y':
            return current_dir.parent
    
    return current_dir


def main():
    """Точка входа"""
    parser = argparse.ArgumentParser(
        description='Умный экспорт Python файла с зависимостями',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s catalog_screen.py          # Экспорт catalog_screen.py с зависимостями
  %(prog)s app/ui/screens/main_screen.py --output custom_export.md
  %(prog)s database.py --full         # Полный экспорт со всеми связями
        """
    )
    
    parser.add_argument(
        'target',
        help='Целевой файл для экспорта (например: catalog_screen.py или app/ui/screens/catalog_screen.py)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Имя выходного файла (если не указано - будет сгенерировано автоматически)'
    )
    
    parser.add_argument(
        '--root', '-r',
        help='Корневая директория проекта (по умолчанию - ищется pyproject.toml)'
    )
    
    parser.add_argument(
        '--full', '-f',
        action='store_true',
        help='Полный анализ зависимостей (может быть медленнее для больших проектов)'
    )
    
    args = parser.parse_args()
    
    print("Умный экспорт файла с зависимостями")
    print("=" * 50)
    
    if args.root:
        project_root = pathlib.Path(args.root).resolve()
        if not project_root.exists():
            print(f"Директория не найдена: {args.root}")
            return
    else:
        project_root = find_pyproject_root()
    
    print(f"Корень проекта: {project_root}")
    print(f"Целевой файл: {args.target}")
    
    exporter = SmartProjectExporter(project_root)
    
    try:
        output_file, file_count = exporter.export_smart(args.target, args.output)
        
        print(f"Экспорт успешно завершен!")
        print(f"Выходной файл: {output_file}")
        print(f"Файлов экспортировано: {file_count}")
        print(f"Зависимостей найдено: {file_count - 1}")
        print("\nЧто содержит экспорт:")
        print("   1. Целевой файл (полное содержимое)")
        print("   2. Все его зависимости (import/from)")
        print("   3. Структуру базы данных (без данных)")
        print("   4. Файлы моделей и работы с БД")
        print("   5. Конфигурационные файлы")
        print("   6. Основные файлы проекта")
        print("   7. Граф зависимостей в текстовом виде")
        print("\nИсключено из экспорта:")
        print("   1. advanced_documentation.py (файл генерации документации)")
        
    except FileNotFoundError as e:
        print(f"{e}")
        print("\nПопробуйте:")
        print(f"   1. Указать полный путь: app/ui/screens/catalog_screen.py")
        print(f"   2. Убедиться, что файл существует в проекте")
        print(f"   3. Проверить текущую директорию: {project_root}")
        
    except Exception as e:
        print(f"Ошибка при экспорте: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
```

### smart_export_short.py
**Размер:** 29028 байт  
```python
import os
import ast
import pathlib
import argparse
from datetime import datetime
from typing import Set, List, Dict, Optional
import re

class SmartProjectExporter:
    """
    !!! Обрезает файлы, нет экспорта БД!!!
    Умный экспорт проекта с зависимостями.
    Экспортирует структуру, целевой файл и все его зависимости.
    """
    
    def __init__(self, root_path="."):
        self.root_path = pathlib.Path(root_path).resolve()
        
        # Директории для исключения
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
            'venv', '.venv', 'env', '.env', 'envs',
            '.vscode', '.idea', 'vs_code',
            'dist', 'build', '*.egg-info',
            'node_modules', 'coverage', '.coverage',
            '.github', '.gitlab', '.bitbucket',
            'generated_docs'  # исключаем документацию
        }
        
        # Файлы для исключения
        self.exclude_files = {
            '*.pyc', '*.pyo', '*.pyd', '*.so',
            '*.db', '*.sqlite', '*.sqlite3', '*.log',
            'poetry.lock', 'package-lock.json', 'yarn.lock',
            '.gitignore', '.env', '.env.local', '.env.*',
            'Thumbs.db', 'desktop.ini', '.DS_Store'
        }
        
        self.import_graph: Dict[str, Set[str]] = {}
        self.analyzed_files: Set[str] = set()
        
    def should_skip(self, path: pathlib.Path) -> bool:
        """Определить, нужно ли пропустить файл/папку"""
        name = path.name
        
        # Пропускаем скрытые файлы
        if name.startswith('.'):
            return True
        
        # Пропускаем исключенные директории
        if path.is_dir():
            for pattern in self.exclude_dirs:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern:
                    return True
        
        # Пропускаем файлы в исключенных директориях
        for parent in path.parents:
            if parent.name in self.exclude_dirs:
                return True
        
        # Пропускаем исключенные файлы по шаблону
        if path.is_file():
            for pattern in self.exclude_files:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern:
                    return True
        
        return False
    
    def analyze_imports(self, file_path: pathlib.Path) -> Set[str]:
        """Анализирует импорты в файле и возвращает зависимости"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Стандартные импорты
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])  # Берем только модуль
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # from module import ...
                        imports.add(node.module.split('.')[0])
                    # from . import something
                    elif node.level > 0:  # Относительный импорт
                        # Находим локальный модуль
                        current_dir = file_path.parent
                        for i in range(node.level - 1):
                            current_dir = current_dir.parent
                        # Ищем файлы с импортируемыми именами
                        for name_obj in node.names:
                            # Пытаемся найти файл
                            possible_names = [
                                f"{name_obj.name}.py",
                                f"{name_obj.name}/__init__.py"
                            ]
                            for possible in possible_names:
                                possible_path = current_dir / possible
                                if possible_path.exists():
                                    rel_path = possible_path.relative_to(self.root_path)
                                    imports.add(str(rel_path).replace('.py', '').replace('/', '.'))
            
            # Анализ строковых импортов (для Kivy, SQLAlchemy и т.д.)
            string_imports = re.findall(r"from\s+['\"](.+?)['\"]", content)
            string_imports += re.findall(r"import\s+['\"](.+?)['\"]", content)
            
            for imp in string_imports:
                imports.add(imp.split('.')[0])
                
        except Exception as e:
            print(f"⚠️  Ошибка анализа {file_path}: {e}")
        
        return imports
    
    def find_dependencies(self, target_file: pathlib.Path) -> Set[pathlib.Path]:
        """Находит все зависимости для целевого файла"""
        all_deps = set()
        to_analyze = {target_file}
        
        print(f"🔍 Поиск зависимостей для {target_file.name}...")
        
        while to_analyze:
            current_file = to_analyze.pop()
            
            if current_file in self.analyzed_files:
                continue
                
            self.analyzed_files.add(current_file)
            
            if not current_file.exists():
                print(f"⚠️  Файл не найден: {current_file}")
                continue
            
            # Анализируем импорты
            imports = self.analyze_imports(current_file)
            self.import_graph[str(current_file.relative_to(self.root_path))] = imports
            
            # Находим файлы для найденных импортов
            for imp in imports:
                found_files = self.find_file_by_import(imp, current_file.parent)
                for found_file in found_files:
                    if found_file not in self.analyzed_files:
                        to_analyze.add(found_file)
                        all_deps.add(found_file)
            
            # Специальные зависимости для типичных структур
            self._add_special_dependencies(current_file, all_deps, to_analyze)
        
        return all_deps
    
    def find_file_by_import(self, import_name: str, search_from: pathlib.Path) -> List[pathlib.Path]:
        """Находит файл по имени импорта"""
        found_files = []
        
        # Пробуем разные варианты
        possible_paths = [
            # Прямой путь из корня проекта
            self.root_path / import_name.replace('.', '/') / '__init__.py',
            self.root_path / f"{import_name.replace('.', '/')}.py",
            
            # Относительно текущего файла
            search_from / f"{import_name}.py",
            search_from / import_name / '__init__.py',
            
            # Для app.module
            self.root_path / 'app' / import_name.replace('.', '/') / '__init__.py',
            self.root_path / 'app' / f"{import_name.replace('.', '/')}.py",
        ]
        
        # Рекурсивный поиск
        for pattern in [f"**/{import_name}.py", f"**/{import_name}/__init__.py"]:
            try:
                for found in self.root_path.glob(pattern):
                    if not self.should_skip(found):
                        found_files.append(found)
            except Exception:
                pass
        
        # Убираем дубликаты и проверяем существование
        unique_files = []
        for file in found_files:
            if file.exists() and file not in unique_files:
                unique_files.append(file)
        
        return unique_files
    
    def _add_special_dependencies(self, current_file: pathlib.Path, 
                                  all_deps: Set[pathlib.Path], 
                                  to_analyze: Set[pathlib.Path]):
        """Добавляет специальные зависимости на основе содержимого файла"""
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            current_rel = str(current_file.relative_to(self.root_path))
            
            # Для файлов с "database" в имени
            if 'database' in current_file.name.lower():
                # Ищем связанные конфиги
                for pattern in ['**/config.py', '**/configs.py', '**/settings.py']:
                    for config_file in self.root_path.glob(pattern):
                        if not self.should_skip(config_file) and config_file not in all_deps:
                            all_deps.add(config_file)
                            to_analyze.add(config_file)
            
            # Для UI файлов
            if any(x in current_rel for x in ['screen', 'widget', 'ui']):
                # Ищем связанные виджеты
                for pattern in ['**/widgets/**/*.py', '**/ui/**/*.py']:
                    for ui_file in self.root_path.glob(pattern):
                        if not self.should_skip(ui_file) and ui_file != current_file:
                            # Проверяем, упоминается ли в коде
                            try:
                                with open(ui_file, 'r', encoding='utf-8') as f_ui:
                                    ui_content = f_ui.read()
                                ui_name = ui_file.stem
                                if ui_name in content or ui_name in current_rel:
                                    all_deps.add(ui_file)
                            except:
                                pass
                
                # Проверяем ссылки на главные файлы
                main_files = ['main.py', 'app.py', '__main__.py']
                for main_file in main_files:
                    main_path = self.root_path / main_file
                    if main_path.exists() and main_path not in all_deps:
                        all_deps.add(main_path)
            
            # Для конфигурационных файлов
            if 'config' in current_file.name.lower():
                # Ищем .env файлы
                for env_file in self.root_path.glob('**/.env*'):
                    if not self.should_skip(env_file):
                        all_deps.add(env_file)
        
        except Exception as e:
            print(f"⚠️  Ошибка при анализе специальных зависимостей {current_file}: {e}")
    
    def export_smart(self, target_file: str, output_file: Optional[str] = None):
        """
        Умный экспорт: целевой файл + все его зависимости
        
        Args:
            target_file: Путь к целевому файлу (например, 'app/ui/screens/catalog_screen.py')
            output_file: Имя выходного файла (если None - генерируется автоматически)
        """
        # Находим целевой файл
        target_path = self.root_path / target_file
        if not target_path.exists():
            # Пробуем найти файл
            found_files = list(self.root_path.glob(f"**/{target_file}"))
            if not found_files:
                raise FileNotFoundError(f"Файл {target_file} не найден в проекте")
            target_path = found_files[0]
            print(f"📁 Найден файл: {target_path.relative_to(self.root_path)}")
        
        # Находим все зависимости
        all_deps = self.find_dependencies(target_path)
        
        # Добавляем сам целевой файл
        files_to_export = {target_path}
        files_to_export.update(all_deps)
        
        # Добавляем основные файлы проекта
        main_files = [
            self.root_path / 'main.py',
            self.root_path / 'pyproject.toml',
            self.root_path / 'requirements.txt',
        ]
        
        for main_file in main_files:
            if main_file.exists():
                files_to_export.add(main_file)
        
        # Генерируем имя выходного файла
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_name = target_path.stem
            output_file = f"SMART_EXPORT_{target_name}_{timestamp}.md"
        
        # Экспортируем
        self._write_export(files_to_export, target_path, output_file)
        
        return output_file, len(files_to_export)
    
    def _write_export(self, files: Set[pathlib.Path], 
                     target_file: pathlib.Path,
                     output_file: str):
        """Записывает экспорт в файл"""
        
        # Сортируем файлы по пути
        sorted_files = sorted(files, key=lambda x: str(x.relative_to(self.root_path)))
        
        with open(output_file, 'w', encoding='utf-8') as out:
            # Заголовок
            target_rel = target_file.relative_to(self.root_path)
            out.write(f"# 🎯 Умный экспорт: {target_rel}\n")
            out.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"**Целевой файл:** `{target_rel}`\n")
            out.write(f"**Проект:** {self.root_path.name}\n\n")
            
            # Обзор зависимостей
            out.write("## 📊 Обзор зависимостей\n\n")
            
            # Граф зависимостей в текстовом виде
            out.write("```\n")
            out.write(f"Целевой файл: {target_rel}\n")
            out.write("Зависимости:\n")
            
            for file in sorted_files:
                if file == target_file:
                    continue
                rel_path = file.relative_to(self.root_path)
                out.write(f"  ├── {rel_path}\n")
            out.write("```\n\n")
            
            # Структура экспортируемых файлов
            out.write("## 📁 Структура экспорта\n\n")
            out.write("```\n")
            
            # Группируем по директориям
            dir_structure = {}
            for file in sorted_files:
                rel_path = file.relative_to(self.root_path)
                parent = str(rel_path.parent)
                if parent == '.':
                    parent = ''
                if parent not in dir_structure:
                    dir_structure[parent] = []
                dir_structure[parent].append(rel_path.name)
            
            # Выводим структуру
            def print_dir(dir_path: str, indent: int = 0):
                if dir_path in dir_structure:
                    prefix = "  " * indent
                    if dir_path:
                        out.write(f"{prefix}{dir_path.split('/')[-1]}/\n")
                    for file in sorted(dir_structure[dir_path]):
                        file_prefix = "  " * (indent + 1)
                        icon = "🎯" if dir_path == str(target_file.parent) and file == target_file.name else "📄"
                        out.write(f"{file_prefix}{icon} {file}\n")
                
                # Поддиректории
                subdirs = []
                if dir_path:
                    # Находим непосредственные поддиректории
                    dir_prefix = dir_path + '/'
                    subdirs = [
                        d for d in dir_structure.keys()
                        if d.startswith(dir_prefix) and dir_prefix.count('/') == d.count('/') - 1
                    ]
                else:
                    # Для корневой директории: все поддиректории первого уровня
                    subdirs = [
                        d for d in dir_structure.keys()
                        if d and '/' not in d
                    ]
                
                # Рекурсивно выводим поддиректории
                for subdir in sorted(set(subdirs)):
                    print_dir(subdir, indent + 1)
                    
            out.write("```\n\n")
            
            # Содержимое файлов
            out.write("## 📝 Содержимое файлов\n\n")
            
            total_size = 0
            file_count = 0
            
            for i, file in enumerate(sorted_files, 1):
                rel_path = file.relative_to(self.root_path)
                
                # Определяем язык для подсветки
                ext = file.suffix.lower()
                lang_map = {
                    '.py': 'python',
                    '.toml': 'toml',
                    '.txt': 'text',
                    '.ini': 'ini',
                    '.cfg': 'ini',
                    '.md': 'markdown',
                    '.json': 'json',
                    '.yml': 'yaml',
                    '.yaml': 'yaml',
                }
                lang = lang_map.get(ext, '')
                
                # Заголовок файла
                icon = "🎯" if file == target_file else "📄"
                out.write(f"### {icon} {rel_path}\n")
                
                if file == target_file:
                    out.write("**🔹 ЦЕЛЕВОЙ ФАЙЛ**  \n")
                
                # Информация о файле
                try:
                    file_size = file.stat().st_size
                    out.write(f"**Размер:** {file_size} байт  \n")
                    total_size += file_size
                    file_count += 1
                    
                    # Импорты для этого файла
                    if str(rel_path) in self.import_graph:
                        imports = self.import_graph[str(rel_path)]
                        if imports:
                            out.write(f"**Импортирует:** `{', '.join(sorted(imports))}`  \n")
                    
                except Exception as e:
                    out.write(f"**Ошибка:** {e}  \n")
                
                # Содержимое файла
                try:
                    # Читаем файл
                    try:
                        content = file.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            content = file.read_text(encoding='cp1251')
                        except:
                            content = f"# ⚠️ Файл в бинарном формате или неизвестной кодировке\n"
                    
                    # Обрезаем слишком большие файлы
                    max_lines = 500
                    lines = content.split('\n')
                    if len(lines) > max_lines:
                        content = '\n'.join(lines[:max_lines])
                        content += f"\n\n# ... файл обрезан, показано {max_lines} из {len(lines)} строк ..."
                    
                    out.write(f"```{lang}\n")
                    out.write(content)
                    if not content.endswith('\n'):
                        out.write('\n')
                    out.write("```\n\n")
                    
                except Exception as e:
                    out.write(f"```\n# ❌ Ошибка при чтении файла: {e}\n```\n\n")
            
            # Статистика
            out.write("## 📈 Статистика экспорта\n\n")
            out.write(f"- **Всего файлов:** {file_count}\n")
            out.write(f"- **Целевой файл:** `{target_rel}`\n")
            out.write(f"- **Зависимостей найдено:** {len(files) - 1}\n")
            out.write(f"- **Общий размер:** {total_size} байт ({total_size/1024:.1f} KB)\n")
            out.write(f"- **Глубина анализа:** {len(self.analyzed_files)} файлов проанализировано\n")
            
            # Рекомендации
            out.write("\n## 💡 Рекомендации по использованию\n\n")
            out.write("1. **Целевой файл** помечен значком 🎯\n")
            out.write("2. Порядок файлов соответствует структуре проекта\n")
            out.write("3. Зависимости включают:\n")
            out.write("   - Прямые импорты (import/from)\n")
            out.write("   - Родственные модули\n")
            out.write("   - Конфигурационные файлы\n")
            out.write("   - Основные файлы проекта (main.py и др.)\n")
            out.write("\n## 🔗 Граф зависимостей (текстовый)\n\n")
            out.write("```\n")
            self._write_dependency_graph(out, target_file)
            out.write("```\n")


    def _write_dependency_graph(self, out, target_file: pathlib.Path):
        """Записывает текстовый граф зависимостей"""
        target_rel = str(target_file.relative_to(self.root_path))
        
        # Собираем граф
        graph = {}
        for file, imports in self.import_graph.items():
            for imp in imports:
                # Находим файлы для этого импорта
                possible_files = []
                for dep_file in self.analyzed_files:
                    dep_rel = str(dep_file.relative_to(self.root_path))
                    if imp in dep_rel.replace('/', '.').replace('.py', ''):
                        possible_files.append(dep_rel)
                
                if possible_files:
                    if file not in graph:
                        graph[file] = []
                    graph[file].extend(possible_files)
        
        # Выводим граф
        out.write(f"{target_rel}\n")
        visited = set()
        
        def print_node(node: str, indent: int = 0):
            if node in visited:
                out.write("  " * indent + f"└── {node} (циклическая ссылка)\n")
                return
                
            visited.add(node)
            
            if node in graph:
                deps = graph[node]
                for i, dep in enumerate(sorted(deps)):
                    prefix = "  " * indent
                    if i == len(deps) - 1:
                        out.write(f"{prefix}└── {dep}\n")
                        print_node(dep, indent + 1)
                    else:
                        out.write(f"{prefix}├── {dep}\n")
                        print_node(dep, indent + 1)
        
        print_node(target_rel)


def find_pyproject_root() -> pathlib.Path:
    """Находит корень проекта по pyproject.toml"""
    current_dir = pathlib.Path.cwd()
    
    # Проверяем текущую директорию
    if (current_dir / "pyproject.toml").exists():
        return current_dir
    
    # Проверяем родительскую
    elif (current_dir.parent / "pyproject.toml").exists():
        print(f"📁 Pyproject.toml найден в родительской папке: {current_dir.parent}")
        choice = input("   Использовать родительскую папку как корень проекта? (y/n): ")
        if choice.lower() == 'y':
            return current_dir.parent
    
    return current_dir


def main():
    """Точка входа"""
    parser = argparse.ArgumentParser(
        description='Умный экспорт Python файла с зависимостями',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s catalog_screen.py          # Экспорт catalog_screen.py с зависимостями
  %(prog)s app/ui/screens/main_screen.py --output custom_export.md
  %(prog)s database.py --full         # Полный экспорт со всеми связями
        """
    )
    
    parser.add_argument(
        'target',
        help='Целевой файл для экспорта (например: catalog_screen.py или app/ui/screens/catalog_screen.py)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Имя выходного файла (если не указано - будет сгенерировано автоматически)'
    )
    
    parser.add_argument(
        '--root', '-r',
        help='Корневая директория проекта (по умолчанию - ищется pyproject.toml)'
    )
    
    parser.add_argument(
        '--full', '-f',
        action='store_true',
        help='Полный анализ зависимостей (может быть медленнее для больших проектов)'
    )
    
    args = parser.parse_args()
    
    print("🔍 Умный экспорт файла с зависимостями")
    print("=" * 50)
    
    # Определяем корень проекта
    if args.root:
        project_root = pathlib.Path(args.root).resolve()
        if not project_root.exists():
            print(f"❌ Директория не найдена: {args.root}")
            return
    else:
        project_root = find_pyproject_root()
    
    print(f"📂 Корень проекта: {project_root}")
    print(f"🎯 Целевой файл: {args.target}")
    
    # Создаем экспортер
    exporter = SmartProjectExporter(project_root)
    
    try:
        # Выполняем экспорт
        output_file, file_count = exporter.export_smart(args.target, args.output)
        
        print(f"✅ Экспорт успешно завершен!")
        print(f"📄 Выходной файл: {output_file}")
        print(f"📊 Файлов экспортировано: {file_count}")
        print(f"🔗 Зависимостей найдено: {file_count - 1}")
        print("\n📋 Что содержит экспорт:")
        print("   1. Целевой файл (помечен 🎯)")
        print("   2. Все его зависимости (import/from)")
        print("   3. Конфигурационные файлы")
        print("   4. Основные файлы проекта")
        print("   5. Граф зависимостей в текстовом виде")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\n💡 Попробуйте:")
        print(f"   1. Указать полный путь: app/ui/screens/catalog_screen.py")
        print(f"   2. Убедиться, что файл существует в проекте")
        print(f"   3. Проверить текущую директорию: {project_root}")
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

## Статистика экспорта

- **Всего файлов:** 16
- **Целевой файл:** `app\ui\screens\catalog_screen.py`
- **Зависимостей найдено:** 15
- **Общий размер:** 235636 байт (230.1 KB)
- **Глубина анализа:** 1 файлов проанализировано

## Рекомендации по использованию

1. **Целевой файл** помечен значком >>>
2. Порядок файлов соответствует структуре проекта
3. **Исключены из экспорта:**
   - Файл advanced_documentation.py (генерация документации)
   - Служебные файлы и директории
4. Зависимости включают:
   - Прямые импорты (import/from)
   - Родственные модули
   - Конфигурационные файлы
   - Основные файлы проекта (main.py и др.)
5. **Структура базы данных** включает:
   - Все таблицы и их колонки
   - Индексы и внешние ключи
   - Файлы моделей и схем

## Граф зависимостей (текстовый)

```
app\ui\screens\catalog_screen.py
```
