# 🎯 Умный экспорт: app\ui\screens\catalog_screen.py
**Дата:** 2025-12-07 18:02:19
**Целевой файл:** `app\ui\screens\catalog_screen.py`
**Проект:** plant_protection_app

## 📊 Обзор зависимостей

```
Целевой файл: app\ui\screens\catalog_screen.py
Зависимости:
  ├── app\ui\__init__.py
  ├── app\ui\screens\__init__.py
  ├── app\ui\screens\substance_editor.py
  ├── app\ui\widgets\__init__.py
  ├── main.py
  ├── pyproject.toml
```

## 📁 Структура экспорта

```
```

## 📝 Содержимое файлов

### 📄 app\ui\__init__.py
**Размер:** 0 байт  
```python

```

### 📄 app\ui\screens\__init__.py
**Размер:** 0 байт  
```python

```

### 🎯 app\ui\screens\catalog_screen.py
**🔹 ЦЕЛЕВОЙ ФАЙЛ**  
**Размер:** 78479 байт  
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

# ... файл обрезан, показано 500 из 1919 строк ...
```

### 📄 app\ui\screens\substance_editor.py
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

### 📄 app\ui\widgets\__init__.py
**Размер:** 0 байт  
```python

```

### 📄 main.py
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

### 📄 pyproject.toml
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

## 📈 Статистика экспорта

- **Всего файлов:** 7
- **Целевой файл:** `app\ui\screens\catalog_screen.py`
- **Зависимостей найдено:** 6
- **Общий размер:** 88957 байт (86.9 KB)
- **Глубина анализа:** 1 файлов проанализировано

## 💡 Рекомендации по использованию

1. **Целевой файл** помечен значком 🎯
2. Порядок файлов соответствует структуре проекта
3. Зависимости включают:
   - Прямые импорты (import/from)
   - Родственные модули
   - Конфигурационные файлы
   - Основные файлы проекта (main.py и др.)

## 🔗 Граф зависимостей (текстовый)

```
app\ui\screens\catalog_screen.py
```
