from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

# Импортируем вкладки из отдельных файлов
from app.ui.screens.settings_screen import SettingsTab
from app.ui.screens.catalog_screen import CatalogTab

Builder.load_string('''
<MainScreen>:
    MDBottomNavigation:
        id: bottom_nav
        panel_color: "#f5f5f5"
        selected_color_background: "#e0f2f1"
        text_color_active: "green"

<DiagnosisTab>:
    name: 'diagnosis'
    text: 'Диагностика'
    icon: 'camera'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        
        MDLabel:
            text: 'Модуль диагностики заболеваний'
            halign: 'center'
            font_style: 'H5'
        
<OrdersTab>:
    name: 'orders'
    text: 'Заказы'
    icon: 'cart'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        
        MDLabel:
            text: 'Управление заказами'
            halign: 'center'
            font_style: 'H5'
''')

# Классы для вкладок навигации
class DiagnosisTab(MDBottomNavigationItem):
    pass

class OrdersTab(MDBottomNavigationItem):
    pass

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_enter(self):
        """Вызывается при переходе на экран"""
        self._setup_navigation()
    
    def _setup_navigation(self):
        """Настройка нижней панели навигации"""
        bottom_nav = self.ids.bottom_nav
        
        # Добавляем вкладки
        bottom_nav.add_widget(DiagnosisTab())
        bottom_nav.add_widget(CatalogTab())  # Используем импортированный класс
        bottom_nav.add_widget(OrdersTab())
        bottom_nav.add_widget(SettingsTab())