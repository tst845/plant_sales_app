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