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