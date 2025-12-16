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