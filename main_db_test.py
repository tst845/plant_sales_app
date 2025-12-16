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