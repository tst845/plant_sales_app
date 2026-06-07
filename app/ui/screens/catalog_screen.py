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
from kivy.clock import Clock
from kivy.properties import DictProperty
# from kivy.animation import Animation
from kivy.uix.widget import Widget 

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
        RecycleView:
            id: pesticide_recycle
            size_hint_y: 1
            viewclass: 'PesticideCard'
            bar_width: dp(5)
            scroll_type: ['bars', 'content']
            RecycleBoxLayout:
                id: recycle_layout
                default_size: None, dp(80)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(5)
                padding: dp(10)        
        
        # Нижняя панель с кнопкой создания
        AnchorLayout:
            size_hint_y: None
            height: "50dp"
            md_bg_color: [0.9, 0.9, 0.9, 1]   # светло-серый
            anchor_x: "center"
            anchor_y: "center"

            MDIconButton:
                icon: "plus"
                theme_icon_color: "Custom"
                icon_color: "white"
                md_bg_color: "green"
                size_hint: None, None
                size: "56dp", "28dp"
                on_release: root.create_new_pesticide()
    
    # # Кнопка экспорта в Excel (слева)
    # MDFloatingActionButton:
        # id: excel_export_btn
    #     icon: "file-excel"
    #     type: "standard"
    #     md_bg_color: "#2196F3"  # Синий цвет для Excel
    #     elevation_normal: 12
    #     pos_hint: {"x": 0.02, "y": 0.02}
    #     size_hint: (None, None)
    #     size: ("56dp", "56dp")
    #     on_release: root.export_to_excel()
                    
    # # Фиксированная кнопка создания поверх списка
    # MDFloatingActionButton:
    #     id: create_pesticide_btn
    #     icon: "plus"
    #     type: "standard"
    #     md_bg_color: "green"
    #     elevation_normal: 12
    #     pos_hint: {"center_x": 0.5, "y": 0.02}
    #     size_hint: (None, None)
    #     size: ("56dp", "56dp")
    #     on_release: root.create_new_pesticide()

<PesticideCard>:
    orientation: 'vertical'
    padding: ['8dp', '4dp', '8dp', '6dp']   # уменьшены вертикальные отступы
    spacing: '4dp'
    size_hint_y: None
    height: '80dp'
    ripple_behavior: True
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: '12dp'
        size_hint_y: 1
        
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.7
            spacing: '2dp'
            
            MDLabel:
                id: name_label
                text: root.pesticide_name
                font_style: 'Subtitle1'
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
                font_style: 'Caption'
                theme_text_color: 'Custom'
                text_color: (0, 0.4, 0, 1)      # тёмно-зелёный (R,G,B,A)
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'left'
                valign: 'top'
                shorten: True
                shorten_from: 'right'
                max_lines: 1
            
            MDLabel:
                id: type_label
                text: root.pesticide_type
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
    spacing: "20dp"
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
    spacing: "10dp"
    padding: "15dp"
    size_hint_y: None
    height: "500dp"

    ScrollView:
        MDBoxLayout:
            orientation: "vertical"
            spacing: "10dp"
            size_hint_y: None
            height: self.minimum_height

            MDLabel:
                text: "Название:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_name
                mode: "rectangle"

            MDLabel:
                text: "Действующие вещества:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_substance
                mode: "rectangle"
                multiline: True
                height: dp(60)
                hint_text: "Пример: ДВ1 1,1 г/л, ДВ2 2,2 г/л"

            MDLabel:
                text: "Описание:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_description
                mode: "rectangle"
                multiline: True
                height: dp(90)

            MDLabel:
                text: "Норма расхода:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_application_rate
                mode: "rectangle"

            MDLabel:
                text: "Фасовка:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_packaging
                mode: "rectangle"

            MDLabel:
                text: "Цена:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_price
                mode: "rectangle"
                input_filter: "float"

            MDLabel:
                text: "Производитель:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_manufacturer
                mode: "rectangle"

            MDLabel:
                text: "Тип пестицида:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_type
                mode: "rectangle"
                hint_text: "Выберите тип..."
                on_focus: if self.focus: root.open_type_menu()

            MDLabel:
                text: "Болезни:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_diseases
                mode: "rectangle"
                multiline: True
                height: dp(60)

            MDLabel:
                text: "Культуры:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_cultures
                mode: "rectangle"
                multiline: True
                height: dp(60)

    MDBoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "10dp"

        MDFlatButton:
            text: "Отмена"
            on_release: root.cancel_edit()

        MDRaisedButton:
            text: "Принять"
            on_release: root.save_pesticide()
        MDRaisedButton:
            text: "Удалить"
            theme_text_color: "Custom"
            text_color: "white"
            md_bg_color: "red"
            on_release: root.delete_pesticide()
            disabled: root.is_new
            opacity: 0 if root.is_new else 1
''')


class PesticideCardData(dict):
    # Просто обёртка, чтобы использовать словари как данные
    pass

class PesticideCard(MDCard):
    pesticide_name = StringProperty("")
    pesticide_substance = StringProperty("")
    pesticide_description = StringProperty("")
    pesticide_price = StringProperty("")
    pesticide_packaging = StringProperty("")
    pesticide_application_rate = StringProperty("")
    pesticide_type = StringProperty("") 
    catalog_instance = ObjectProperty(None)
    full_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        print("Создаётся PesticideCard")
        super().__init__(**kwargs)
        # self.block_scroll = False
        # print("Атрибуты:", dir(self))

    def apply_data(self, data_dict):
        """Обновить карточку из словаря данных"""
        self.pesticide_name = data_dict.get('name', '')
        self.pesticide_description = data_dict.get('description', '')
        self.pesticide_price = data_dict.get('price', '')
        self.pesticide_packaging = data_dict.get('packaging', '')
        self.pesticide_application_rate = data_dict.get('application_rate', '')
        self.pesticide_substance = data_dict.get('substances', '')
        self.pesticide_type = data_dict.get('pesticide_type', '') 
        self.catalog_instance = data_dict.get('catalog_instance')
        # сохраним id и другие данные для обработчика on_release
        self.pesticide_data = data_dict
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.catalog_instance:
            self.catalog_instance.show_pesticide_details(self.full_data)
            return True
        return super().on_touch_up(touch)
    
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
    is_new = BooleanProperty(False)
    def __init__(self, catalog_instance, pesticide_data, **kwargs):
        self.catalog_instance = catalog_instance
        self.pesticide_data = pesticide_data
        self.type_menu = None
        # флаг, новый ли препарат
        self.is_new = not pesticide_data.get('name', '')
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        if not hasattr(self, 'ids'):
            return
        data = self.pesticide_data
        self.ids.edit_name.text = data.get('name', '')
        raw = data.get('substances', '')
        if raw and raw != 'None':
            formatted = self.catalog_instance._format_substances(raw)
            self.ids.edit_substance.text = formatted.replace('\n', ', ')
        else:
            self.ids.edit_substance.text = ''
        self.ids.edit_description.text = data.get('description', '')
        self.ids.edit_application_rate.text = data.get('application_rate', '')
        self.ids.edit_packaging.text = data.get('packaging', '')
        price = data.get('price', '')
        if isinstance(price, (int, float)):
            price = str(price)
        self.ids.edit_price.text = price
        self.ids.edit_manufacturer.text = data.get('manufacturer', '')
        self.ids.edit_type.text = data.get('type', data.get('pesticide_type', 'Гербициды'))

        # Загружаем культуры и болезни для существующего препарата
        if 'id' in data and data['id']:
            app = MDApp.get_running_app()
            cursor = app.db.connection.cursor()
            cursor.execute('''
                SELECT c.culture_name
                FROM pesticide_cultures pc
                JOIN cultures c ON pc.culture_id = c.id
                WHERE pc.pesticide_id = ?
            ''', (data['id'],))
            cultures_list = [row['culture_name'] for row in cursor.fetchall()]
            cursor.execute('''
                SELECT d.disease_name
                FROM pesticide_diseases pd
                JOIN diseases d ON pd.disease_id = d.id
                WHERE pd.pesticide_id = ?
            ''', (data['id'],))
            diseases_list = [row['disease_name'] for row in cursor.fetchall()]
            self.ids.edit_cultures.text = ', '.join(cultures_list) if cultures_list else ''
            self.ids.edit_diseases.text = ', '.join(diseases_list) if diseases_list else ''
        else:
            self.ids.edit_cultures.text = ''
            self.ids.edit_diseases.text = ''

    def open_type_menu(self):
        if self.type_menu and self.type_menu.parent:
            self.type_menu.dismiss()
            self.type_menu = None
            return
        pesticide_types = ["Гербициды", "Инсектициды", "Фунгициды", "Бактерициды", "Фумиганты"]
        menu_items = [
            {"text": t, "viewclass": "OneLineListItem", "height": dp(48),
             "on_release": lambda x=t: self.select_pesticide_type(x)} for t in pesticide_types
        ]
        self.type_menu = MDDropdownMenu(
            caller=self.ids.edit_type,
            items=menu_items,
            width=dp(200),
            max_height=dp(150),
            position="auto",
            ver_growth="down"
        )
        self.type_menu.open()

    def select_pesticide_type(self, ptype):
        self.ids.edit_type.text = ptype
        if self.type_menu:
            self.type_menu.dismiss()
            self.type_menu = None

    def save_pesticide(self):
        # Собираем данные из полей
        data = {
            'name': self.ids.edit_name.text,
            'substances': self.ids.edit_substance.text,   # сырая строка
            'description': self.ids.edit_description.text,
            'application_rate': self.ids.edit_application_rate.text,
            'packaging': self.ids.edit_packaging.text,
            'price': self.ids.edit_price.text,
            'manufacturer': self.ids.edit_manufacturer.text,
            'type': self.ids.edit_type.text,
            'diseases': self.ids.edit_diseases.text,
            'cultures': self.ids.edit_cultures.text,
        }
        if self.is_new:
            self.catalog_instance.save_new_pesticide(data)
        else:
            if 'id' in self.pesticide_data:
                data['id'] = self.pesticide_data['id']
            self.catalog_instance.save_pesticide_changes(data)
        # Передаём в каталог
        self.catalog_instance.save_pesticide_changes(data)
        # Закрываем меню, если открыто
        if self.type_menu:
            self.type_menu.dismiss()
            self.type_menu = None

    def cancel_edit(self):
        if self.type_menu:
            self.type_menu.dismiss()
            self.type_menu = None
        self.catalog_instance.cancel_edit()

    def delete_pesticide(self):
        self.catalog_instance.delete_pesticide(self.pesticide_data)

    def on_dismiss(self):
        if self.type_menu:
            self.type_menu.dismiss()
            self.type_menu = None
            

class CatalogTab(MDBottomNavigationItem):
    app = ObjectProperty(None)
    restoring_scroll = BooleanProperty(False) # Добавьте флаг, чтобы on_recycle_scroll игнорировал изменения, вызванные программной установкой scroll_y:
    visible_count = 0          # сколько элементов показываем в RecycleView
    data = []                  # все загруженные элементы (полные словари)
    CARD_HEIGHT = dp(80)       # высота одной карточки
    SPACING = dp(5)            # spacing из разметки
    ITEM_HEIGHT = CARD_HEIGHT + SPACING  # полная высота, занимаемая одним элементом в лейауте
    LOAD_THRESHOLD = ITEM_HEIGHT * 2     # начинаем подгрузку, когда до конца осталось 2 карточки
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
        self.confirm_dialog = None
        self.edit_dialog = None
        self.current_editing_pesticide = None
        self.selected_types = []
        self.selected_cultures = []
        self.selected_diseases = []

        self.data = []                 # все загруженные препараты (словари)
        self.current_offset = 0
        self.saved_scroll_offset = 0.0
        self.limit = 10
        self.loading = False
        self.is_end_reached = False
        self.search_query = ""

        self.opening_details = False
        
        # Инициализация test_pesticides (ЗДЕСЬ ИСПРАВЛЕНИЕ!)
        self.test_pesticides = self._get_test_pesticides()
    
        try:
            import pandas as pd
            import openpyxl
            import os
            from datetime import datetime
        except ImportError as e:
            print(f"⚠️ Библиотеки для экспорта не установлены: {e}")
    
    def refresh_data(self):
        self.current_offset = 0
        self.data = []
        self.visible_count = 0
        self.is_end_reached = False
        self.loading = False
        rv = self.ids.pesticide_recycle
        rv.data = []
        rv.scroll_y = 1.0
        self._perform_load()
    
    def load_more(self):
    # Предотвращаем множественные вызовы
        if self.loading or self.is_end_reached:
            return
        self._perform_load()
        
    def _perform_load(self):
        if self.loading or self.is_end_reached:
            return
        self.loading = True
        print(f"Загрузка offset={self.current_offset}, limit={self.limit}")

        rv = self.ids.pesticide_recycle
        viewport_height = rv.height

        # Сохраняем пиксельное смещение перед изменением данных
        if self.visible_count > 0 and rv.children:
            content_height = rv.children[0].height
            if content_height > viewport_height:
                self.saved_scroll_offset = (1.0 - rv.scroll_y) * (content_height - viewport_height)
            else:
                self.saved_scroll_offset = 0.0
        else:
            self.saved_scroll_offset = 0.0

        try:
            app = MDApp.get_running_app()
            new_items = app.db.get_pesticides_paginated(
                offset=self.current_offset,
                limit=self.limit,
                search=self.search_query,
                filters=self.filters,
                sort_by=self.sort_settings['criteria'],
                sort_order=self.sort_settings['order']
            )
            if not new_items:
                self.is_end_reached = True
                self.loading = False
                return

            for item in new_items:
                card_dict = {
                    'pesticide_name': item.get('name', ''),
                    'pesticide_description': item.get('description', ''),
                    'pesticide_price': self._format_price(item.get('price', 0)),
                    'pesticide_packaging': item.get('packaging', ''),
                    'pesticide_application_rate': item.get('application_rate', ''),
                    'pesticide_substance': self._format_substances(item.get('substances', '')),
                    'pesticide_type': item.get('pesticide_type', 'Не указан'),  
                    'substances': item.get('substances', ''),
                    'catalog_instance': self, 
                    'full_data': item,
                }
                self.data.append(card_dict)

            self.current_offset += len(new_items)
            if len(new_items) < self.limit:
                self.is_end_reached = True

            # Увеличиваем видимый диапазон
            if self.visible_count == 0:
                self.visible_count = min(len(self.data), 10)
            else:
                self.visible_count = min(self.visible_count + 3, len(self.data))

            rv.data = self.data[:self.visible_count]

            if self.visible_count > 10:          # не первая загрузка
                Clock.schedule_once(lambda dt: self._restore_scroll_position(viewport_height), 0)
            else:
                rv.scroll_y = 1.0

        except Exception as e:
            print(f"Ошибка загрузки: {e}")
        finally:
            self.loading = False
    
    def _show_more(self):
        if self.visible_count >= len(self.data):
            return

        rv = self.ids.pesticide_recycle
        viewport_height = rv.height

        if rv.children:
            content_height = rv.children[0].height
            if content_height > viewport_height:
                self.saved_scroll_offset = (1.0 - rv.scroll_y) * (content_height - viewport_height)
            else:
                self.saved_scroll_offset = 0.0
        else:
            self.saved_scroll_offset = 0.0

        self.visible_count = min(self.visible_count + 3, len(self.data))
        rv.data = self.data[:self.visible_count]

        Clock.schedule_once(lambda dt: self._restore_scroll_position(viewport_height), 0)    
    

    def _format_price(self, price):
        if isinstance(price, (int, float)):
            return f"{int(price)} руб."
        return str(price) if price else 'Цена не указана'

    def _parse_substances(self, composition_str):
        if not composition_str:
            return []
        import re
        # Заменяем ", " и ";" и "+" на единый разделитель ";"
        s = re.sub(r', ', ';', composition_str)          # запятая с пробелом
        s = re.sub(r'\s*[+;]\s*', ';', s)                # плюс или точка с запятой
        fragments = s.split(';')
        result = []
        conc_pattern = re.compile(r'([\d,\.]+\s*(?:г/кг|г/л|%|мг/кг|мг/л))')

        for frag in fragments:
            frag = frag.strip()
            if not frag:
                continue
            match = conc_pattern.search(frag)
            if match:
                conc = match.group(1).strip()
                name = (frag[:match.start()].strip() + " " + frag[match.end():].strip()).strip()
                if not name and result:
                    name = result[-1][0]
                if name:   # добавляем только если есть название
                    result.append((name, conc))
            else:
                if result:
                    last_name, last_conc = result[-1]
                    result[-1] = (f"{last_name} {frag}".strip(), last_conc)
                else:
                    result.append((frag, ''))
        # Удаляем дубликаты
        seen = set()
        unique = []
        for name, conc in result:
            key = (name, conc)
            if key not in seen:
                seen.add(key)
                unique.append((name, conc))
        return unique

    def _format_substances(self, substances_str):
        if not substances_str or substances_str == 'None':
            return "Действующие вещества не указаны"
        parts = substances_str.split('||')
        formatted = [part.strip() for part in parts if part.strip()]
        # print('def _format_substances formatted: ', formatted)
        return ', '.join(formatted) if formatted else "Действующие вещества не указаны"

    def _restore_scroll_position(self, viewport_height):
        rv = self.ids.pesticide_recycle
        if not rv.children:
            return
        new_content_height = rv.children[0].height
        if new_content_height <= viewport_height:
            new_scroll_y = 1.0
        else:
            new_scroll_y = 1.0 - (self.saved_scroll_offset / (new_content_height - viewport_height))
            new_scroll_y = max(0.0, min(1.0, new_scroll_y))

        self.restoring_scroll = True
        rv.scroll_y = new_scroll_y
        self.restoring_scroll = False


    def on_recycle_scroll(self, instance, value):
        if self.loading or self.is_end_reached or self.restoring_scroll:
            return

        rv = self.ids.pesticide_recycle
        if not rv.children:
            return

        content_height = rv.children[0].height
        viewport_height = rv.height
        if content_height <= viewport_height:
            return

        scroll_offset = (1.0 - value) * (content_height - viewport_height)
        distance_to_end = content_height - viewport_height - scroll_offset

        if distance_to_end < self.LOAD_THRESHOLD:
            if self.visible_count < len(self.data):
                self._show_more()
                # Блокируем повторные вызовы на короткое время
                self.restoring_scroll = True
                Clock.schedule_once(lambda dt: setattr(self, 'restoring_scroll', False), 0.3)
            elif not self.is_end_reached:
                self.load_more()

    def on_enter(self):
        self._setup_catalog()
        self.bind_scroll()

    def bind_scroll(self):
        recycle = self.ids.pesticide_recycle
        recycle.bind(scroll_y=self.on_recycle_scroll)
    
    def _setup_catalog(self):
        """Настройка каталога"""
        self.refresh_data()
    
    def clear_search(self):
        """Очистить поиск"""
        self.ids.search_input.text = ""
        self.refresh_data()
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
        if hasattr(self.ids, 'search_clear_button'):
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
        self.refresh_data()
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
            ),
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
         
        self.edit_dialog.open()

    def confirm_delete_pesticide(self, pesticide):
        """Диалог подтверждения удаления препарата"""
        self.confirm_dialog = MDDialog(
            title="Удаление препарата",
            text=f"Удалить препарат «{pesticide.get('name', '')}»?\nЭто действие нельзя отменить.",
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda x: self.confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Удалить",
                    md_bg_color=(1, 0, 0, 1),  # красный
                    on_release=lambda x: self._on_confirm_delete(pesticide)
                ),
            ],
        )
        self.confirm_dialog.open()

    def _on_confirm_delete(self, pesticide):
        """Действие при подтверждении удаления"""
        self.confirm_dialog.dismiss()
        if self.detail_dialog:
            self.detail_dialog.dismiss()
        self.delete_pesticide(pesticide)

    def set_diagnosis_filters(self, species_list, disease_list):
        """Установить фильтры по культурам и болезням из результатов диагностики."""
        print(f"DEBUG: set_diagnosis_filters called with species={species_list}, diseases={disease_list}")
        self.filters = {}
        self.selected_cultures = []
        self.selected_diseases = []

        app = MDApp.get_running_app()
        cursor = app.db.connection.cursor()

        existing_cultures = []
        for name in species_list:
            cursor.execute("SELECT id FROM cultures WHERE culture_name = ?", (name,))
            row = cursor.fetchone()
            print(f"DEBUG: culture '{name}' found: {row is not None}")
            if row:
                existing_cultures.append(name)
        if existing_cultures:
            self.selected_cultures = existing_cultures
            self.filters['cultures'] = existing_cultures

        existing_diseases = []
        for name in disease_list:
            cursor.execute("SELECT id FROM diseases WHERE disease_name = ?", (name,))
            row = cursor.fetchone()
            print(f"DEBUG: disease '{name}' found: {row is not None}")
            if row:
                existing_diseases.append(name)
        if existing_diseases:
            self.selected_diseases = existing_diseases
            self.filters['diseases'] = existing_diseases

        print("DEBUG: final filters =", self.filters)
        self.refresh_data()
    
    def search_pesticides(self, query):
        """Поиск препаратов"""
        print(f"🔍 Поиск: {query}")
        # Обновляем цвет крестика
        if hasattr(self, 'search_clear_button'):
            if query:
                self.search_clear_button.icon_color = "gray"
            else:
                self.search_clear_button.icon_color = [0.5, 0.5, 0.5, 0.3]
        self.search_query = query
        self.refresh_data()
    
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
        self.refresh_data()
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
        if self.type_menu and self.type_menu.parent:
            self.type_menu.dismiss()
            self.type_menu = None
            return
        pesticide_types = ["Гербициды", "Инсектициды", "Фунгициды", "Бактерициды", "Фумиганты"]
        menu_items = [{"text": t, "viewclass": "OneLineListItem", "height": dp(48),
                    "on_release": lambda x=t: self.select_pesticide_type(x)} for t in pesticide_types]
        self.type_menu = MDDropdownMenu(
            caller=self.filter_dialog.content_cls.ids.type_filter,
            items=menu_items,
            width=dp(200),
            max_height=dp(150),
            position="auto",
            ver_growth="down"
        )
        self.type_menu.open()

    def open_culture_menu(self):
        """Открыть меню выбора культур для фильтрации"""
        if not self.filter_dialog:
            return
        if self.culture_menu and self.culture_menu.parent:
            self.culture_menu.dismiss()
            self.culture_menu = None
            return
        
        # Список доступных культур (можно загружать из БД)
        # cultures = ["Пшеница", "Ячмень", "Кукуруза", "Подсолнечник", "Соя", "Рапс", "Сахарная свекла", "Картофель"]
         # Загружаем реальные культуры
        app = MDApp.get_running_app()
        cursor = app.db.connection.cursor()
        cursor.execute("SELECT culture_name FROM cultures ORDER BY culture_name")
        cultures = [row['culture_name'] for row in cursor.fetchall()]
        menu_items = [
            {
                "text": culture,
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda x=culture: self.select_culture(x),
            } for culture in cultures
        ]
        
        self.culture_menu = MDDropdownMenu(
            caller=self.filter_dialog.content_cls.ids.culture_filter,
            items=menu_items,
            width=dp(200),
            max_height=dp(150),
            position="auto",
            ver_growth="down"
        )
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

    def save_new_pesticide(self, new_data):
        if not new_data.get('name'):
            self._show_error_message("Название препарата обязательно!")
            return
        try:
            app = MDApp.get_running_app()
            db = app.db
            cursor = db.connection.cursor()

            # Определяем type_id
            type_name = new_data.get('type', 'Гербициды')
            cursor.execute("SELECT id FROM pesticide_types WHERE type_name = ?", (type_name,))
            res = cursor.fetchone()
            if not res:
                cursor.execute("INSERT INTO pesticide_types (type_name) VALUES (?)", (type_name,))
                type_id = cursor.lastrowid
            else:
                type_id = res['id']

            # Вставляем препарат
            cursor.execute('''
                INSERT INTO pesticides (name, description, application_rate, packaging, price, manufacturer, pesticide_type_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                new_data['name'],
                new_data.get('description', ''),
                new_data.get('application_rate', ''),
                new_data.get('packaging', ''),
                new_data.get('price', '0').replace(',', '.'),
                new_data.get('manufacturer', ''),
                type_id
            ))
            pesticide_id = cursor.lastrowid

            # Вставляем действующие вещества
            substances_str = new_data.get('substances', '')
            if substances_str:
                substances = self._parse_substances(substances_str)
                seen = set()
                for substance_name, concentration in substances:
                    if not substance_name:
                        continue
                    key = (substance_name, concentration)
                    if key in seen:
                        continue
                    seen.add(key)
                    cursor.execute("SELECT id FROM active_substances WHERE substance_name = ?", (substance_name,))
                    res = cursor.fetchone()
                    if not res:
                        cursor.execute("INSERT INTO active_substances (substance_name) VALUES (?)", (substance_name,))
                        substance_id = cursor.lastrowid
                    else:
                        substance_id = res['id']
                    cursor.execute("INSERT INTO pesticide_active_substances (pesticide_id, substance_id, concentration) VALUES (?, ?, ?)",
                                (pesticide_id, substance_id, concentration))

            # Культуры
            cultures_str = new_data.get('cultures', '')
            if cultures_str:
                culture_list = [c.strip() for c in cultures_str.split(',') if c.strip()]
                for cult_name in culture_list:
                    cursor.execute("SELECT id FROM cultures WHERE culture_name = ?", (cult_name,))
                    res = cursor.fetchone()
                    if not res:
                        cursor.execute("INSERT INTO cultures (culture_name) VALUES (?)", (cult_name,))
                        culture_id = cursor.lastrowid
                    else:
                        culture_id = res['id']
                    cursor.execute("INSERT OR IGNORE INTO pesticide_cultures (pesticide_id, culture_id) VALUES (?, ?)", (pesticide_id, culture_id))

            # Болезни
            diseases_str = new_data.get('diseases', '')
            if diseases_str:
                disease_list = [d.strip() for d in diseases_str.split(',') if d.strip()]
                for dis_name in disease_list:
                    cursor.execute("SELECT id FROM diseases WHERE disease_name = ?", (dis_name,))
                    res = cursor.fetchone()
                    if not res:
                        cursor.execute("INSERT INTO diseases (disease_name) VALUES (?)", (dis_name,))
                        disease_id = cursor.lastrowid
                    else:
                        disease_id = res['id']
                    cursor.execute("INSERT OR IGNORE INTO pesticide_diseases (pesticide_id, disease_id) VALUES (?, ?)", (pesticide_id, disease_id))

            db.connection.commit()

            self._show_success_message(f"Препарат '{new_data['name']}' создан")
            if self.edit_dialog:
                self.edit_dialog.dismiss()
                 
            self.refresh_data()
        except Exception as e:
            print(f"❌ Ошибка создания препарата: {e}")
            self._show_error_message(f"Ошибка создания: {e}")

    # def open_disease_menu(self):
    #     """Открыть меню выбора заболеваний ПОД полем"""
    #     if not self.filter_dialog:
    #         return
    #     if self.disease_menu and self.disease_menu.parent:
    #         self.disease_menu.dismiss()
    #         self.disease_menu = None
    #         return
        
    #     # Список доступных заболеваний (можно загружать из БД)
    #     diseases = [
    #         "Мучнистая роса", "Парша", "Ржавчина", "Фитофтороз", "Антракноз",
    #         "Бактериальная пятнистость", "Вирус мозаики", "Серая гниль", "Черная пятнистость"
    #     ]
        
    #     menu_items = [
    #         {
    #             "text": disease,
    #             "viewclass": "OneLineListItem",
    #             "height": dp(48),
    #             "on_release": lambda x=disease: self.select_disease(x),
    #         } for disease in diseases
    #     ]
        
    #     self.disease_menu = MDDropdownMenu(
    #         caller=self.filter_dialog.content_cls.ids.disease_filter,
    #         items=menu_items,
    #         width=dp(200),
    #         max_height=dp(150),
    #         position="auto",
    #         ver_growth="down"
    #     )
    #     self.disease_menu.open()
    def open_disease_menu(self):
        if not self.filter_dialog:
            return
        if self.disease_menu and self.disease_menu.parent:
            self.disease_menu.dismiss()
            self.disease_menu = None
            return
        app = MDApp.get_running_app()
        cursor = app.db.connection.cursor()
        cursor.execute("SELECT disease_name FROM diseases ORDER BY disease_name")
        diseases = [row['disease_name'] for row in cursor.fetchall()]
        menu_items = [
            {"text": d, "viewclass": "OneLineListItem", "height": dp(48),
            "on_release": lambda x=d: self.select_disease(x)} for d in diseases
        ]
        self.disease_menu = MDDropdownMenu(
            caller=self.filter_dialog.content_cls.ids.disease_filter,
            items=menu_items,
            width=dp(200),
            max_height=dp(150),
            position="auto",
            ver_growth="down"
        )
        self.disease_menu.open()

    def select_culture(self, culture):
        """Выбрать культуру в фильтрах (добавить/удалить)"""
        if not self.filter_dialog:
            return
        content = self.filter_dialog.content_cls
        current = content.ids.culture_filter.text
        items = [c.strip() for c in current.split(',') if c.strip()]
        if culture in items:
            items.remove(culture)
        else:
            items.append(culture)
        content.ids.culture_filter.text = ', '.join(items)
        self.selected_cultures = items.copy()   # синхронизация
        if self.culture_menu:
            self.culture_menu.dismiss()
            self.culture_menu = None

    def select_disease(self, disease):
        """Выбрать заболевание в фильтрах (добавить/удалить)"""
        if not self.filter_dialog:
            return
        content = self.filter_dialog.content_cls
        current = content.ids.disease_filter.text
        items = [d.strip() for d in current.split(',') if d.strip()]
        if disease in items:
            items.remove(disease)
        else:
            items.append(disease)
        content.ids.disease_filter.text = ', '.join(items)
        self.selected_diseases = items.copy()   # синхронизация
        if self.disease_menu:
            self.disease_menu.dismiss()
            self.disease_menu = None
            
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
        
            
    def show_pesticide_details(self, pesticide):
        if self.detail_dialog and self.detail_dialog.parent:
            return
        if self.opening_details:
            return
        self.opening_details = True
        try:
            pesticide_data = pesticide if isinstance(pesticide, dict) else dict(pesticide)
            print(f"📋 Детали препарата: {pesticide_data.get('name', 'Unknown')}")
            self.current_editing_pesticide = pesticide_data
    # Получаем культуры и болезни из БД
            app = MDApp.get_running_app()
            cursor = app.db.connection.cursor()

            cultures_list = []
            if 'id' in pesticide_data:
                cursor.execute('''
                    SELECT c.culture_name
                    FROM pesticide_cultures pc
                    JOIN cultures c ON pc.culture_id = c.id
                    WHERE pc.pesticide_id = ?
                ''', (pesticide_data['id'],))
                cultures_list = [row['culture_name'] for row in cursor.fetchall()]

            diseases_list = []
            if 'id' in pesticide_data:
                cursor.execute('''
                    SELECT d.disease_name
                    FROM pesticide_diseases pd
                    JOIN diseases d ON pd.disease_id = d.id
                    WHERE pd.pesticide_id = ?
                ''', (pesticide_data['id'],))
                diseases_list = [row['disease_name'] for row in cursor.fetchall()]

            cultures_str = ", ".join(cultures_list) if cultures_list else "Не указаны"
            diseases_str = ", ".join(diseases_list) if diseases_list else "Не указаны"

            # Действующие вещества (как раньше)
            raw_substances = pesticide_data.get('substances', '')
            substances_text = self._format_substances(raw_substances)
            if not substances_text:
                substances_text = "Действующие вещества не указаны"
            else:
                substances_text = substances_text.replace('\n', ', ')

            pesticide_type = pesticide_data.get('pesticide_type', pesticide_data.get('type', 'Не указано'))
            price = pesticide_data.get('price', '')
            if isinstance(price, (int, float)):
                price_display = f"{int(price)} руб."
            else:
                price_display = str(price) if price else 'Не указана'

            # detail_text = f"""[color=000000]
    # [b]Действующие вещества:[/b]
    # {substances_text}


    # [b]Описание:[/b]
    # {pesticide_data.get('description', 'Не указано')}

    # [b]Норма расхода:[/b] {pesticide_data.get('application_rate', 'Не указано')}
    # [b]Фасовка:[/b] {pesticide_data.get('packaging', 'Не указано')}
    # [b]Цена:[/b] {price_display}
    # [b]Производитель:[/b] {pesticide_data.get('manufacturer', 'Не указано')}

    # [b]Тип пестицида:[/b] {pesticide_type}

    # [b]Культуры:[/b]
    # {cultures_str}

    # [b]Болезни:[/b]
    # {diseases_str}
    # [/color]"""
            detail_text = f"""
    Действующие вещества:
    {substances_text}

    Описание:
    {pesticide_data.get('description', 'Не указано')}

    Норма расхода: {pesticide_data.get('application_rate', 'Не указано')}
    Фасовка: {pesticide_data.get('packaging', 'Не указано')}
    Цена: {price_display}
    Производитель: {pesticide_data.get('manufacturer', 'Не указано')}

    Тип пестицида: {pesticide_type}

    Культуры:
    {cultures_str}

    Болезни:
    {diseases_str}
    """

            # Создаём метку с явным размером шрифта (например, 14sp)
            from kivy.metrics import sp
            label = MDLabel(
                text=detail_text,
                font_size=sp(14),
                halign='left',
                valign='top',
                size_hint_y=None,
                padding=(10, 10)
            )
            # label.font_name = 'Roboto'
            label.bind(texture_size=label.setter('size'))
            
            # # Создаём прокручиваемую метку
            # label = MDLabel(
            #     text=detail_text,          # detail_text уже содержит BB-разметку
            #     markup=True, 
            #     size_hint_y=None,
            #     halign='left',
            #     valign='top',
            #     padding=(10, 10)
            # )
            # label.bind(texture_size=label.setter('size'))
            scroll = ScrollView(size_hint=(1, 1))
            scroll.add_widget(label)

            # Контейнер с фиксированной высотой, чтобы диалог не схлопнулся
            container = MDBoxLayout(orientation='vertical', size_hint_y=None, height=dp(350))
            container.add_widget(scroll)    

            buttons = [
                MDIconButton(
                    icon="close",
                    theme_icon_color="Custom",
                    icon_color="red",
                    on_release=lambda x: self.detail_dialog.dismiss() if self.detail_dialog else None
                ),
            ]
            if 'id' in pesticide_data:
                buttons.insert(1, MDIconButton(
                    icon="pencil-outline",
                    theme_icon_color="Custom",
                    icon_color="green",
                    on_release=lambda x, pd=pesticide_data: self.edit_pesticide(pd)
                ))
                #  кнопка «Удалить»
                buttons.insert(2, MDIconButton(
                    icon="delete",
                    theme_icon_color="Custom",
                    icon_color="red",
                    on_release=lambda x, pd=pesticide_data: self.confirm_delete_pesticide(pd)
                ))

            self.detail_dialog = MDDialog(
                title=pesticide_data.get('name', 'Без названия'),
                type="custom",
                content_cls=container,       
                size_hint=(0.9, 0.8),
                buttons=buttons
            )
            self.detail_dialog.open()
        finally:
            self.opening_details = False

   
    def edit_pesticide(self, pesticide):
        if hasattr(self, 'detail_dialog') and self.detail_dialog:
            self.detail_dialog.dismiss()
        self.current_editing_pesticide = pesticide
        self.edit_dialog = MDDialog(
            title="Редактирование препарата",
            type="custom",
            content_cls=EditPesticideDialog(
                catalog_instance=self,
                pesticide_data=pesticide
            ),
            size_hint=(0.9, 0.9),
            auto_dismiss=False
        )
         
        self.edit_dialog.open()

   
    def _edit_substances(self):
        """Редактирование действующих веществ"""
        if self.current_editing_pesticide and self.current_editing_pesticide.get('id'):
            # Закрываем диалог редактирования
            if self.edit_dialog:
                self.edit_dialog.dismiss()
            
            # Открываем редактор ДВ
            self.app.show_substance_editor(self.current_editing_pesticide['id'])

    # def _save_pesticide_edit(self):
    #     """Сохранение изменений препарата (вызывается из диалога)"""
    #     try:
    #         dialog = self.edit_dialog.content_cls  # сам EditPesticideDialog
    #         updated_pesticide = {
    #             'name': dialog.ids.edit_name.text,
    #             'description': dialog.ids.edit_description.text,
    #             'application_rate': dialog.ids.edit_application_rate.text,
    #             'packaging': dialog.ids.edit_packaging.text,
    #             'price': float(dialog.ids.edit_price.text) if dialog.ids.edit_price.text else 0.0,
    #             'manufacturer': dialog.ids.edit_manufacturer.text,
    #             'pesticide_type': dialog.ids.edit_type.text
    #         }
    #         # Если это существующий препарат, добавляем id
    #         if self.current_editing_pesticide and 'id' in self.current_editing_pesticide:
    #             updated_pesticide['id'] = self.current_editing_pesticide['id']

    #         print(f"💾 Сохранены изменения препарата: {updated_pesticide['name']}")
    #         # Здесь должен быть реальный UPDATE в БД
    #         self.edit_dialog.dismiss()
    #         self.refresh_data()
    #     except Exception as e:
    #         print(f"❌ Ошибка сохранения препарата: {e}")

    def save_pesticide_changes(self, updated_data):
        try:
            app = MDApp.get_running_app()
            db = app.db
            cursor = db.connection.cursor()

            pesticide_id = updated_data.get('id')
            if not pesticide_id:
                return  # новый препарат пока не поддерживается, но можно добавить

            # Обновляем основные поля препарата
            cursor.execute('''
                UPDATE pesticides 
                SET name = ?, description = ?, application_rate = ?, packaging = ?, 
                    price = ?, manufacturer = ?, pesticide_type_id = (
                        SELECT id FROM pesticide_types WHERE type_name = ?
                    )
                WHERE id = ?
            ''', (
                updated_data['name'],
                updated_data['description'],
                updated_data['application_rate'],
                updated_data['packaging'],
                updated_data['price'].replace(',', '.') if updated_data['price'] else '0',
                updated_data['manufacturer'],
                updated_data['type'],
                pesticide_id
            ))

            # Обновляем действующие вещества
            substances_str = updated_data.get('substances', '')
            # Удаляем старые связи
            cursor.execute("DELETE FROM pesticide_active_substances WHERE pesticide_id = ?", (pesticide_id,))
            if substances_str:
                # Парсим строку так же, как при импорте
                substances = self._parse_substances(substances_str)   # нужно добавить этот метод в CatalogTab
                seen = set()
                for substance_name, concentration in substances:
                    if not substance_name:
                        continue
                    key = (substance_name, concentration)
                    if key in seen:
                        continue
                    seen.add(key)
                    cursor.execute("SELECT id FROM active_substances WHERE substance_name = ?", (substance_name,))
                    res = cursor.fetchone()
                    if not res:
                        cursor.execute("INSERT INTO active_substances (substance_name) VALUES (?)", (substance_name,))
                        substance_id = cursor.lastrowid
                    else:
                        substance_id = res[0]
                    cursor.execute("INSERT INTO pesticide_active_substances (pesticide_id, substance_id, concentration) VALUES (?, ?, ?)",
                                (pesticide_id, substance_id, concentration))

            # Обновляем культуры и болезни (аналогично, можно сделать позже)
            # Пока оставим заглушки или тоже обновим
            # Например, для культур:
            if 'cultures' in updated_data:
                cursor.execute("DELETE FROM pesticide_cultures WHERE pesticide_id = ?", (pesticide_id,))
                culture_list = [c.strip() for c in updated_data['cultures'].split(',') if c.strip()]
                for cult_name in culture_list:
                    cursor.execute("SELECT id FROM cultures WHERE culture_name = ?", (cult_name,))
                    res = cursor.fetchone()
                    if not res:
                        cursor.execute("INSERT INTO cultures (culture_name) VALUES (?)", (cult_name,))
                        culture_id = cursor.lastrowid
                    else:
                        culture_id = res[0]
                    cursor.execute("INSERT OR IGNORE INTO pesticide_cultures (pesticide_id, culture_id) VALUES (?, ?)", (pesticide_id, culture_id))

            # Болезни – аналогично
            if 'diseases' in updated_data:
                cursor.execute("DELETE FROM pesticide_diseases WHERE pesticide_id = ?", (pesticide_id,))
                disease_list = [d.strip() for d in updated_data['diseases'].split(',') if d.strip()]
                for dis_name in disease_list:
                    cursor.execute("SELECT id FROM diseases WHERE disease_name = ?", (dis_name,))
                    res = cursor.fetchone()
                    if not res:
                        cursor.execute("INSERT INTO diseases (disease_name) VALUES (?)", (dis_name,))
                        disease_id = cursor.lastrowid
                    else:
                        disease_id = res[0]
                    cursor.execute("INSERT OR IGNORE INTO pesticide_diseases (pesticide_id, disease_id) VALUES (?, ?)", (pesticide_id, disease_id))

            db.connection.commit()
            # Закрываем диалог
            if self.edit_dialog:
                self.edit_dialog.dismiss()
                 
            self.refresh_data()
            self._show_success_message(f"Препарат '{updated_data['name']}' обновлён")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            self._show_error_message(f"Ошибка сохранения: {e}")
    
    def delete_pesticide(self, pesticide):
        """Удалить препарат из базы данных"""
        pesticide_id = pesticide.get('id')
        if not pesticide_id:
            return
        try:
            app = MDApp.get_running_app()
            db = app.db
            cursor = db.connection.cursor()
            # Удаляем связанные записи (каскадное удаление не настроено)
            cursor.execute("DELETE FROM pesticide_active_substances WHERE pesticide_id = ?", (pesticide_id,))
            cursor.execute("DELETE FROM pesticide_cultures WHERE pesticide_id = ?", (pesticide_id,))
            cursor.execute("DELETE FROM pesticide_diseases WHERE pesticide_id = ?", (pesticide_id,))
            cursor.execute("DELETE FROM pesticides WHERE id = ?", (pesticide_id,))
            db.connection.commit()
            print(f"🗑️ Препарат '{pesticide.get('name', '')}' удалён из БД")
            self._show_success_message(f"Препарат '{pesticide.get('name', '')}' удалён")
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            self._show_error_message(f"Ошибка удаления: {e}")
        finally:
            # Закрываем диалог редактирования, если открыт
            if self.edit_dialog:
                self.edit_dialog.dismiss()
                 
            self.refresh_data()
    
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
    
    # def add_to_order(self, pesticide):
    #     """Добавить препарат в заказ"""
    #     print(f"🛒 Добавлен в заказ: {pesticide['name']}")
    #     if self.detail_dialog:
    #         self.detail_dialog.dismiss()
        
    #     self.show_snackbar(f"Препарат '{pesticide['name']}' добавлен в заказ")
       
    def select_pesticide_type(self, pesticide_type):
        """Выбрать тип пестицида в фильтрах"""
        try:
            if not self.filter_dialog:
                return
            content = self.filter_dialog.content_cls
            current = content.ids.type_filter.text
            types = [t.strip() for t in current.split(',') if t.strip()]
            if pesticide_type in types:
                types.remove(pesticide_type)
            else:
                types.append(pesticide_type)
            content.ids.type_filter.text = ', '.join(types)
            self.selected_types = types.copy()   # синхронизация
            if self.type_menu:
                self.type_menu.dismiss()
                self.type_menu = None
        except Exception as e:
            print(f"❌ Ошибка выбора типа в фильтрах: {e}")
   
    def apply_filters(self):
        """Применить фильтры"""
        if self.filter_dialog:
            content = self.filter_dialog.content_cls
            self.filters = {
                'type': getattr(self, 'selected_types', []).copy(),
                'cultures': getattr(self, 'selected_cultures', []).copy(),
                'diseases': getattr(self, 'selected_diseases', []).copy(),
                'min_price': content.ids.min_price.text,
                'max_price': content.ids.max_price.text
            }
            # self.filters = {
            #     'type': self.selected_types.copy(),
            #     'cultures': self.selected_cultures.copy(),
            #     'diseases': self.selected_diseases.copy(),
            #     'min_price': content.ids.min_price.text,
            #     'max_price': content.ids.max_price.text
            # }
            print(f"✅ Применены фильтры: {self.filters}")
            self.refresh_data()
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
        self.refresh_data()
    
    
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

    def export_to_excel(self):
        """Экспорт отфильтрованного списка препаратов в Excel"""
        try:
            print("📊 Начинаю экспорт в Excel...")
            
            # Импортируем необходимые библиотеки
            import pandas as pd
            import os
            from datetime import datetime
            from kivy import platform
            
            # Определяем путь для сохранения файла
            if platform == 'android':
                # На Android сохраняем во внешнее хранилище
                from android.storage import primary_external_storage_path
                base_path = primary_external_storage_path()
                export_dir = os.path.join(base_path, "Documents", "PlantProtection")
            else:
                # На компьютере сохраняем в папку проекта
                export_dir = os.path.join(os.getcwd(), "exports")
            
            # Создаем директорию если ее нет
            os.makedirs(export_dir, exist_ok=True)
            
            # Генерируем имя файла с датой и временем
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pesticides_export_{timestamp}.xlsx"
            filepath = os.path.join(export_dir, filename)
            
            # Получаем отфильтрованные препараты
            filtered_pesticides = []
            
            # Получаем данные из БД или тестовые данные
            app = MDApp.get_running_app()
            if hasattr(app.db, 'get_pesticides_with_substances'):
                try:
                    pesticides = app.db.get_pesticides_with_substances()
                    # Применяем фильтры
                    # filtered_pesticides = self._apply_filters(pesticides, 
                    #                                          self.ids.search_input.text, 
                    #                                          self.filters)
                except Exception as e:
                    print(f"⚠️ Ошибка получения данных из БД: {e}")
                    filtered_pesticides = self._get_filtered_test_pesticides()
            else:
                filtered_pesticides = self._get_filtered_test_pesticides()
            
            if not filtered_pesticides:
                self._show_error_message("Нет данных для экспорта")
                return
            
            # Подготавливаем данные для экспорта
            excel_data = []
            
            for pesticide in filtered_pesticides:
                # Получаем все действующие вещества для этого препарата
                substances_list = []
                
                if hasattr(pesticide, 'get') and 'substances' in pesticide:
                    substances_str = str(pesticide.get('substances', ''))
                    if substances_str and substances_str != 'None':
                        substances_parts = substances_str.split('||')
                        for substance in substances_parts:
                            if substance.strip():
                                substances_list.append(substance.strip())
                
                # Формируем строку ДВ через точку с запятой
                substances_display = '; '.join(substances_list) if substances_list else 'Не указаны'
                
                # Форматируем цену
                price = pesticide.get('price', '')
                if isinstance(price, (int, float)):
                    price_display = f"{price} руб."
                else:
                    price_display = str(price) if price else 'Не указана'
                
                # Создаем строку для Excel
                row = {
                    'ID': pesticide.get('id', ''),
                    'Название': pesticide.get('name', ''),
                    'Действующие вещества': substances_display,
                    'Описание': pesticide.get('description', ''),
                    'Норма расхода': pesticide.get('application_rate', ''),
                    'Фасовка': pesticide.get('packaging', ''),
                    'Цена': price_display,
                    'Производитель': pesticide.get('manufacturer', ''),
                    'Тип': pesticide.get('type', pesticide.get('pesticide_type', '')),
                    'Культуры': pesticide.get('cultures', ''),
                    'Заболевания': pesticide.get('diseases', ''),
                    'Единица измерения': pesticide.get('unit', '')
                }
                excel_data.append(row)
            
            # Создаем DataFrame
            df = pd.DataFrame(excel_data)
            
            # Экспортируем в Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Препараты', index=False)
                
                # Настраиваем ширину колонок
                worksheet = writer.sheets['Препараты']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Максимальная ширина 50 символов
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Сообщение об успехе
            message = f"✅ Экспортировано {len(excel_data)} препаратов\nФайл: {filename}"
            
            # Показываем диалог с информацией
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.button import MDFlatButton
            
            self.export_dialog = MDDialog(
                title="Экспорт завершен",
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.export_dialog.dismiss()
                    )
                ]
            )
            self.export_dialog.open()
            
            print(f"✅ Экспорт завершен: {filepath}")
            
        except ImportError as e:
            self._show_error_message(f"Библиотеки не установлены: {e}\nУстановите: pip install pandas openpyxl")
        except Exception as e:
            print(f"❌ Ошибка экспорта в Excel: {e}")
            self._show_error_message(f"Ошибка экспорта: {str(e)[:100]}")
    
    def _get_filtered_test_pesticides(self):
        """Получить отфильтрованные тестовые препараты"""
        # Применяем фильтры к тестовым данным
        filtered = self.test_pesticides
        
        # Поиск по названию, описанию и веществу
        search_query = self.ids.search_input.text
        if search_query:
            search_query = search_query.lower()
            filtered = [p for p in filtered
                       if search_query in p.get('name', '').lower()
                       or search_query in p.get('description', '').lower()
                       or search_query in str(p.get('substance', '')).lower()]
        
        # Фильтр по типу
        if self.filters and self.filters.get('type'):
            filtered = [p for p in filtered if p.get('type', '') in self.filters['type']]
        
        # Фильтр по культурам
        if self.filters and self.filters.get('cultures'):
            selected_cultures = self.filters['cultures']
            filtered = [p for p in filtered if any(
                culture in str(p.get('cultures', '')) 
                for culture in selected_cultures
            )]
        
        # Фильтр по заболеваниям
        if self.filters and self.filters.get('diseases'):
            selected_diseases = self.filters['diseases']
            filtered = [p for p in filtered if any(
                disease in str(p.get('diseases', '')) 
                for disease in selected_diseases
            )]
        
        # Фильтр по цене
        if self.filters:
            min_price = self.filters.get('min_price')
            max_price = self.filters.get('max_price')
            
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
    
    def _extract_price(self, price_str):
        """Извлечение числового значения цены из строки"""
        try:
            if isinstance(price_str, (int, float)):
                return float(price_str)
            
            # Убираем все нецифровые символы кроме точки и запятой
            price_str = str(price_str)
            # Убираем текст "руб." и пробелы
            price_str = price_str.replace('руб.', '').replace(' ', '')
            # Заменяем запятую на точку если нужно
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except (ValueError, AttributeError):
            return 0.0
    
    # Вспомогательный метод для показа сообщений
    def show_snackbar(self, message):
        """Показать уведомление"""
        try:
            snackbar = Snackbar(text=message)
            snackbar.open()
        except Exception as e:
            print(f"💬 {message}")