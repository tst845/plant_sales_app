from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

# Импортируем вкладки из отдельных файлов
from app.ui.screens.settings_screen import SettingsTab
from app.ui.screens.catalog_screen import CatalogTab
# from app.ui.screens.orders_screen import OrdersTab
from app.ui.screens.camera_screen import CameraScreen 

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

# <OrdersTab>:
#     name: 'orders'
#     text: 'Заказы'
#     icon: 'cart'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        

''')

# Классы для вкладок навигации
class DiagnosisTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Создаем и добавляем экран камеры при инициализации
        camera_screen = CameraScreen()
        self.add_widget(camera_screen)



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
        bottom_nav.add_widget(CatalogTab())
        # bottom_nav.add_widget(OrdersTab())
        bottom_nav.add_widget(SettingsTab())

    def set_diagnosis_filters(self, species_list, disease_list):
        """Передать фильтры в CatalogTab и переключить вкладку"""
        bottom_nav = self.ids.bottom_nav
        # Найти вкладку CatalogTab по имени (name='catalog')
        for child in bottom_nav.children:
            if hasattr(child, 'name') and child.name == 'catalog':
                child.set_diagnosis_filters(species_list, disease_list)
                break
        bottom_nav.switch_tab('catalog')
    
    def _setup_navigation(self):
        bottom_nav = self.ids.bottom_nav
        self.catalog_tab = CatalogTab()
        bottom_nav.add_widget(DiagnosisTab())
        bottom_nav.add_widget(self.catalog_tab)
        bottom_nav.add_widget(SettingsTab())

    def switch_to_catalog_with_filters(self, species_list, disease_list):
        if self.catalog_tab:
            self.catalog_tab.set_diagnosis_filters(species_list, disease_list)
            # Принудительно обновляем каталог с новыми фильтрами
            self.catalog_tab.refresh_data()
        self.ids.bottom_nav.switch_tab('catalog')