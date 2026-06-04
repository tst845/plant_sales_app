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
                # -- Таблица классов видов (растений)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS species_classes (
                class_index INTEGER PRIMARY KEY,      -- индекс из модели (0..11)
                name_en TEXT NOT NULL,                -- английское название (Apple, Tomato...)
                name_ru TEXT NOT NULL                 -- русское название (Яблоня, Томат...)
            )
        ''')

            # -- Таблица классов болезней
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_classes (
                class_index INTEGER PRIMARY KEY,      -- индекс из модели (0..26)
                name_en TEXT NOT NULL,                -- английское название (apple scab, ...)
                name_ru TEXT NOT NULL                 -- русское название (Парша яблони, ...)
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
        self._load_classes_from_files()
    
    def _load_classes_from_files(self):
        """Загружает species_classes и disease_classes из файлов в папке assets"""
        import csv
        from pathlib import Path
        
        base_dir = Path(__file__).parent.parent.parent
        species_file = base_dir / "app" / "assets" / "data" / "species_classes.txt"
        disease_file = base_dir / "app" / "assets" / "data" / "disease_classes.txt"
        
        # Загрузка видов
        if species_file.exists():
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM species_classes')
            with open(species_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        idx, en, ru = parts
                        cursor.execute('INSERT INTO species_classes (class_index, name_en, name_ru) VALUES (?, ?, ?)', (idx, en, ru))
            self.connection.commit()
            print("✅ Загружены виды из файла")
        else:
            print("⚠️ Файл species_classes.txt не найден")
        
        # Загрузка Заболеваний
        if disease_file.exists():
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM disease_classes')
            with open(disease_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        idx, en, ru = parts
                        cursor.execute('INSERT INTO disease_classes (class_index, name_en, name_ru) VALUES (?, ?, ?)', (idx, en, ru))
            self.connection.commit()
            print("✅ Загружены виды из файла")
        else:
            print("⚠️ Файл disease_classes.txt не найден")
        

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
            WHERE d.disease_class_index = ?
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
    print(f"Поиск по '{query}', фильтры {filters} пока не применяются")
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

