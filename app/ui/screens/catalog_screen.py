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
from kivy.uix.widget import Widget 
from kivy.metrics import sp
import pandas as pd
import os

from kivy.utils import platform

if platform == 'android':
    from plyer import filechooser
else:
    import tkinter.filedialog as filedialog
    import tkinter as Tk

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
        
        # Нижняя панель с кнопкой создания и экспорта 
        BoxLayout:
            size_hint_y: None
            height: "50dp"
            md_bg_color: [0.9, 0.9, 0.9, 1]   # светло-серый

            AnchorLayout:
                size_hint_x: 0.5
                anchor_x: "left"
                anchor_y: "center"
                padding: [dp(10), 0, 0, 0]

                MDIconButton:
                    icon: "file-excel"
                    theme_icon_color: "Custom"
                    icon_color: "white"
                    md_bg_color: "blue"
                    size_hint: None, None
                    size: "56dp", "28dp"
                    on_release: root.confirm_export()

            AnchorLayout:
                size_hint_x: 0.5
                anchor_x: "right"
                anchor_y: "center"
                padding: [0, 0, dp(10), 0]

                MDIconButton:
                    icon: "plus"
                    theme_icon_color: "Custom"
                    icon_color: "white"
                    md_bg_color: "green"
                    size_hint: None, None
                    size: "56dp", "28dp"
                    on_release: root.create_new_pesticide()

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
    spacing: "12dp"
    padding: "10dp"
    size_hint_y: None
    height: "450dp"

    # Тип пестицида
    MDBoxLayout:
        orientation: "vertical"
        spacing: "2dp"
        MDLabel:
            text: "Тип пестицида:"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]
        MDBoxLayout:
            orientation: "horizontal"
            spacing: "5dp"
            MDTextField:
                id: type_filter
                hint_text: "Выберите типы..."
                mode: "rectangle"
                size_hint_x: 0.85
                on_focus: if self.focus: root.catalog_instance.open_type_menu()
            MDIconButton:
                icon: "close-circle"
                size_hint: None, None
                size: "24dp", "24dp"
                theme_icon_color: "Custom"
                icon_color: "gray"
                on_release: root.catalog_instance.clear_type_filter()

    # Культуры
    MDBoxLayout:
        orientation: "vertical"
        spacing: "2dp"
        MDLabel:
            text: "Культуры:"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]
        MDBoxLayout:
            orientation: "horizontal"
            spacing: "5dp"
            MDTextField:
                id: culture_filter
                hint_text: "..."
                mode: "rectangle"
                size_hint_x: 0.85
                on_focus: if self.focus: root.catalog_instance.open_culture_menu()
            MDIconButton:
                icon: "close-circle"
                size_hint: None, None
                size: "24dp", "24dp"
                theme_icon_color: "Custom"
                icon_color: "gray"
                on_release: root.catalog_instance.clear_culture_filter()

    # Заболевания
    MDBoxLayout:
        orientation: "vertical"
        spacing: "2dp"
        MDLabel:
            text: "Заболевания:"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]
        MDBoxLayout:
            orientation: "horizontal"
            spacing: "5dp"
            MDTextField:
                id: disease_filter
                hint_text: "..."
                mode: "rectangle"
                size_hint_x: 0.85
                on_focus: if self.focus: root.catalog_instance.open_disease_menu()
            MDIconButton:
                icon: "close-circle"
                size_hint: None, None
                size: "24dp", "24dp"
                theme_icon_color: "Custom"
                icon_color: "gray"
                on_release: root.catalog_instance.clear_disease_filter()

    # Цена
    MDBoxLayout:
        orientation: "vertical"
        spacing: "3dp"
        MDLabel:
            text: "Цена"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: '5dp'
            size_hint_y: None
            height: '48dp'
            MDTextField:
                id: min_price
                hint_text: "min"
                mode: "rectangle"
                input_filter: 'float'
            MDTextField:
                id: max_price
                hint_text: "max"
                mode: "rectangle"
                input_filter: 'float'
            MDIconButton:
                icon: "close-circle"
                size_hint: None, None
                size: "24dp", "24dp"
                theme_icon_color: "Custom"
                icon_color: "gray"
                on_release: root.catalog_instance.clear_price_filters()

    AnchorLayout:
        size_hint_y: None
        height: "48dp"
        anchor_x: "center"
        anchor_y: "center"
        MDBoxLayout:
            orientation: "horizontal"
            spacing: "10dp"
            size_hint: None, None
            size: self.minimum_size
            MDFlatButton:
                text: "Сбросить"
                theme_text_color: "Custom"
                text_color: "white"
                md_bg_color: "green"
                on_release: root.reset_filters()
            MDRaisedButton:
                text: "Применить"
                theme_text_color: "Custom"
                text_color: "white"
                md_bg_color: "green"
                on_release: root.apply_filters()

<SortDialog>:
    orientation: "vertical"
    spacing: "15dp"
    padding: "10dp"
    size_hint_y: None
    height: "250dp"

    # Критерий сортировки
    MDLabel:
        text: "Критерий сортировки:"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: self.texture_size[1]

    MDBoxLayout:
        orientation: "horizontal"
        spacing: "10dp"
        size_hint_y: None
        height: "40dp"

        MDBoxLayout:
            orientation: "horizontal"
            spacing: "5dp"
            size_hint_x: 0.5
            MDLabel:
                text: "Цена"
                size_hint_y: None
                height: "30dp"
                valign: "middle"
                halign: "right"
            MDCheckbox:
                group: 'sort_criteria'
                id: sort_price
                size_hint: None, None
                size: "30dp", "30dp"
                on_active: root.set_sort_criteria('price')

        MDBoxLayout:
            orientation: "horizontal"
            spacing: "5dp"
            size_hint_x: 0.5
            MDLabel:
                text: "Название"
                size_hint_y: None
                height: "30dp"
                valign: "middle"
                halign: "right"
            MDCheckbox:
                group: 'sort_criteria'
                id: sort_name
                size_hint: None, None
                size: "30dp", "30dp"
                on_active: root.set_sort_criteria('name')

    MDLabel:
        text: "Порядок сортировки:"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: self.texture_size[1]

    MDBoxLayout:
        orientation: "horizontal"
        spacing: "20dp"
        size_hint_y: None
        height: "40dp"

        MDBoxLayout:
            orientation: "horizontal"
            spacing: "5dp"
            size_hint_x: 0.5
            MDLabel:
                text: "Возрастание"
                size_hint_y: None
                height: "30dp"
                valign: "middle"
                halign: "right"
            MDCheckbox:
                group: 'sort_order'
                id: sort_asc
                size_hint: None, None
                size: "30dp", "30dp"
                on_active: root.set_sort_order('asc')

        MDBoxLayout:
            orientation: "horizontal"
            spacing: "5dp"
            size_hint_x: 0.5
            MDLabel:
                text: "Убывание"
                size_hint_y: None
                height: "30dp"
                valign: "middle"
                halign: "right"
            MDCheckbox:
                group: 'sort_order'
                id: sort_desc
                size_hint: None, None
                size: "30dp", "30dp"
                on_active: root.set_sort_order('desc')

    # Кнопки по центру
    AnchorLayout:
        size_hint_y: None
        height: "48dp"
        anchor_x: "center"
        anchor_y: "center"
        MDBoxLayout:
            orientation: "horizontal"
            spacing: "10dp"
            size_hint: None, None
            size: self.minimum_size

            MDFlatButton:
                text: " Отмена"
                theme_text_color: "Custom"
                text_color: "white"
                md_bg_color: "green"
                on_release: root.cancel_sort()

            MDRaisedButton:
                text: "Применить"
                theme_text_color: "Custom"
                text_color: "white"
                md_bg_color: "green"
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
            spacing: "5dp"
            size_hint_y: None
            height: self.minimum_height

            MDLabel:
                text: "Название:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)      
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_name
                mode: "rectangle"

            MDLabel:
                text: "Действующие вещества:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_substance
                mode: "rectangle"
                multiline: True
                height: dp(60)
                hint_text: "Пример: ДВ1 1,1 г/л, ДВ2 2,2 г/л"
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Описание:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_description
                mode: "rectangle"
                multiline: True
                height: dp(90)
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Норма расхода:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_application_rate
                mode: "rectangle"
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Фасовка:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_packaging
                mode: "rectangle"
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Цена:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_price
                mode: "rectangle"
                input_filter: "float"
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Производитель:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_manufacturer
                mode: "rectangle"
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Тип пестицида:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_type
                mode: "rectangle"
                hint_text: "..."
                on_focus: if self.focus: root.open_type_menu()
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Болезни:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_diseases
                mode: "rectangle"
                multiline: True
                height: dp(60)
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Культуры:"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: edit_cultures
                mode: "rectangle"
                multiline: True
                height: dp(60)
                text_color: (0, 0, 0, 1)

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
            disabled: root.is_new
            opacity: 0 if root.is_new else 1

        MDRaisedButton:
            text: "Принять"
            theme_text_color: "Custom"
            text_color: "white"
            md_bg_color: "green"
            on_release: root.save_pesticide()

                    
        MDFlatButton:
            text: "Отмена"
            theme_text_color: "Custom"
            text_color: "white"
            md_bg_color: "green"
            on_release: root.cancel_edit()
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
        self._touch_down_pos = None
        # self.block_scroll = False
        # print("Атрибуты:", dir(self))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_down_pos = (touch.x, touch.y)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._touch_down_pos:
            dx = touch.x - self._touch_down_pos[0]
            dy = touch.y - self._touch_down_pos[1]
            if (dx*dx + dy*dy) < 400:  # порог ~20 пикселей
                if self.catalog_instance:
                    self.catalog_instance.show_pesticide_details(self.full_data)
                    self._touch_down_pos = None
                    return True
        self._touch_down_pos = None
        return super().on_touch_up(touch)

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
    
    def _open_file_dialog(self, title, filters, on_success):
        if platform == 'android':
            android_filters = [f[1] for f in filters]
            filechooser.open_file(
                title=title,
                filters=android_filters,
                on_selection=lambda sel: self._on_file_selected(sel, on_success)
            )
        else:
            root = Tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(title=title, filetypes=filters)
            root.destroy()
            if file_path:
                on_success(file_path)

    def _save_file_dialog(self, title, filters, default_name, on_success):
        if platform == 'android':
            android_filters = [f[1] for f in filters]
            filechooser.save_file(
                title=title,
                filters=android_filters,
                filename=default_name,
                on_selection=lambda sel: self._on_file_selected(sel, on_success)
            )
        else:
            root = Tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.asksaveasfilename(
                title=title,
                defaultextension=".xlsx",
                filetypes=filters,
                initialfile=default_name
            )
            root.destroy()
            if file_path:
                on_success(file_path)

    def _on_file_selected(self, selection, callback):
        if selection and len(selection) > 0:
            callback(selection[0])


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
                app_rate = item.get('application_rate', '')
                if app_rate:
                    pack = item.get('packaging', '').lower()
                    if 'л' in pack:
                        app_rate += " л/га"
                    elif 'кг' in pack:
                        app_rate += " кг/га"
                card_dict = {
                    'pesticide_name': item.get('name', ''),
                    'pesticide_description': item.get('description', ''),
                    'pesticide_price': self._format_price(item.get('price', 0)),
                    'pesticide_packaging': item.get('packaging', ''),
                    'pesticide_application_rate': app_rate,
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
    
    def clear_type_filter(self):
        self.selected_types = []
        if self.filter_dialog:
            self.filter_dialog.content_cls.ids.type_filter.text = ""
        # self.apply_filters()

    def clear_culture_filter(self):
        self.selected_cultures = []
        if self.filter_dialog:
            self.filter_dialog.content_cls.ids.culture_filter.text = ""
        # self.apply_filters()

    def clear_disease_filter(self):
        self.selected_diseases = []
        if self.filter_dialog:
            self.filter_dialog.content_cls.ids.disease_filter.text = ""
        # self.apply_filters()

    def clear_price_filters(self):
        if self.filter_dialog:
            content = self.filter_dialog.content_cls
            content.ids.min_price.text = ""
            content.ids.max_price.text = ""
        # self.apply_filters()

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
            return "ДВ не указаны"
        parts = substances_str.split('||')
        formatted = [part.strip() for part in parts if part.strip()]
        return ', '.join(formatted) if formatted else "ДВ не указаны"

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
            size_hint=(0.9, None),
            height="400dp"
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

            
            rate_str = pesticide_data.get('application_rate', '')
            if rate_str:
                pack = pesticide_data.get('packaging', '').lower()
                if 'л' in pack:
                    rate_str += " л/га"
                elif 'кг' in pack:
                    rate_str += " кг/га"
                else:  rate_str+='Не указано'
            # Действующие вещества (как раньше)
            raw_substances = pesticide_data.get('substances', '')
            if raw_substances and raw_substances != 'None':
                parts = raw_substances.split('||')
                formatted_parts = []
                for part in parts:
                    part = part.strip()
                    if part:
                        formatted_parts.append(part)
                if formatted_parts:
                    # Первая строка с веществом остаётся как есть
                    substances_text ='\n    '+ formatted_parts[0]
                    # Добавляем остальные вещества с отступом
                    for part in formatted_parts[1:]:
                        substances_text += ",\n    " + part   # 4 пробела для выравнивания
                else:
                    substances_text = "Действующие вещества не указаны"
            else:
                substances_text = "Действующие вещества не указаны"

            pesticide_type = pesticide_data.get('pesticide_type', pesticide_data.get('type', 'Не указано'))
            price = pesticide_data.get('price', '')
            if isinstance(price, (int, float)):
                price_display = f"{int(price)} руб."
            else:
                price_display = str(price) if price else 'Не указана'


            detail_text = (
    f"[color=006400]Действующие вещества:[/color]    {substances_text}\n\n"
    f"[color=006400]Описание:[/color]\n{pesticide_data.get('description', 'Не указано')}\n\n"
    f"[color=006400]Норма расхода:[/color] {rate_str}\n"
    f"[color=006400]Фасовка:[/color] {pesticide_data.get('packaging', 'Не указано')}\n"
    f"[color=006400]Цена:[/color] {price_display}\n"
    f"[color=006400]Производитель:[/color] {pesticide_data.get('manufacturer', 'Не указано')}\n\n"
    f"[color=006400]Тип пестицида:[/color] {pesticide_type}\n\n"
    f"[color=006400]Культуры:[/color] {cultures_str}\n\n"
    f"[color=006400]Болезни:[/color] {diseases_str}"
)

            label = MDLabel(
                text=detail_text,
                markup=True,  
                font_style="Subtitle1", # H6 Subtitle1
                theme_text_color="Custom", 
                text_color=(0, 0, 0, 1), 
                halign='left',
                valign='top',
                size_hint_y=None,
                padding=(10, 10)
            )
            # label.font_name = 'Roboto'
            label.bind(texture_size=label.setter('size'))
            
            scroll = ScrollView(
                # size_hint=(1, 1)
                )
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


    def confirm_export(self):
        """Показать диалог подтверждения экспорта с текущими параметрами и количеством"""
        # Предварительно определим количество препаратов (без пагинации)
        try:
            app = MDApp.get_running_app()
            pesticides = app.db.get_pesticides_paginated(
                offset=0,
                limit=100000,
                search=self.search_query,
                filters=self.filters,
                sort_by=self.sort_settings['criteria'],
                sort_order=self.sort_settings['order']
            )
            total_count = len(pesticides) if pesticides else 0
        except Exception as e:
            print(f"Ошибка при подсчёте: {e}")
            total_count = 0

        # Формируем список активных параметров
        params = []
        if self.search_query:
            params.append(f"Поиск: '{self.search_query}'")
        if self.sort_settings['criteria'] == 'price':
            order = "возрастание" if self.sort_settings['order'] == 'asc' else "убывание"
            params.append(f"Сортировка: по цене ({order})")
        else:
            order = "возрастание" if self.sort_settings['order'] == 'asc' else "убывание"
            params.append(f"Сортировка: по названию ({order})")
        if self.filters:
            if 'type' in self.filters and self.filters['type']:
                params.append(f"Тип: {', '.join(self.filters['type'])}")
            if 'cultures' in self.filters and self.filters['cultures']:
                params.append(f"Культуры: {', '.join(self.filters['cultures'])}")
            if 'diseases' in self.filters and self.filters['diseases']:
                params.append(f"Болезни: {', '.join(self.filters['diseases'])}")
            if 'min_price' in self.filters and self.filters['min_price']:
                params.append(f"Цена от: {self.filters['min_price']}")
            if 'max_price' in self.filters and self.filters['max_price']:
                params.append(f"Цена до: {self.filters['max_price']}")

        param_text = "\n".join(params) if params else "Без параметров (весь каталог)"

        import os
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"catalog_export_{timestamp}.xlsx"

        # Создаём контент диалога с чёрным текстом
        content = MDBoxLayout(orientation='vertical', spacing='10dp', padding='10dp', size_hint_y=None)
        content.height = dp(200)

        label = MDLabel(
            text=(
                f"Будет экспортировано препаратов: [color=ff0000]{total_count}[/color]\n\n"
                f"Активные параметры:\n{param_text}\n\n"
                f"Имя файла: {filename}"
            ),
            markup=True,
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
        )
        label.bind(texture_size=label.setter('size'))
        content.add_widget(label)

        self.export_confirm_dialog = MDDialog(
            title="Экспорт каталога",
            type="custom",
            content_cls=content,
            size_hint=(0.9, 0.5),
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    theme_text_color="Custom",
                    text_color="white",
                    md_bg_color="green",
                    on_release=lambda x: self.export_confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Сохранить",
                    theme_text_color="Custom",
                    text_color="white",
                    md_bg_color="green",
                    on_release=lambda x: self._start_export()
                ),
            ],
        )
        self.export_confirm_dialog.open()

    def _start_export(self):
        """Закрыть диалог подтверждения и запустить экспорт, если есть данные"""
        # Проверяем количество
        try:
            app = MDApp.get_running_app()
            pesticides = app.db.get_pesticides_paginated(
                offset=0,
                limit=100000,
                search=self.search_query,
                filters=self.filters,
                sort_by=self.sort_settings['criteria'],
                sort_order=self.sort_settings['order']
            )
            if not pesticides:
                # Показываем сообщение поверх диалога, но не закрываем его
                if self.export_confirm_dialog:
                    # Создаём диалог с сообщением и крестиком
                    self.empty_data_dialog = MDDialog(
                        title="Экспорт",
                        text="Нет данных для сохранения с текущими параметрами.",
                        buttons=[
                            MDIconButton(
                                icon="close",
                                theme_icon_color="Custom",
                                icon_color="red",
                                on_release=lambda x: self.empty_data_dialog.dismiss()
                            )
                        ],
                    )
                    self.empty_data_dialog.open()
                return
        except Exception as e:
            print(f"Ошибка при проверке данных: {e}")
            self._show_error_message("Ошибка при проверке данных")
            return

        if self.export_confirm_dialog:
            self.export_confirm_dialog.dismiss()
        self.export_to_excel()

    def export_to_excel(self):
        """Экспорт каталога в Excel с учётом текущих фильтров, поиска и сортировки"""
        try:
            app = MDApp.get_running_app()
            pesticides = app.db.get_pesticides_paginated(
                offset=0,
                limit=100000,
                search=self.search_query,
                filters=self.filters,
                sort_by=self.sort_settings['criteria'],
                sort_order=self.sort_settings['order']
            )
            if not pesticides:
                self._show_error_message("Нет данных для экспорта")
                return

            cursor = app.db.connection.cursor()
            data_rows = []

            for pest in pesticides:
                pid = pest['id']
                cursor.execute('''
                    SELECT a.substance_name, pas.concentration
                    FROM pesticide_active_substances pas
                    JOIN active_substances a ON pas.substance_id = a.id
                    WHERE pas.pesticide_id = ?
                ''', (pid,))
                substances_list = [f"{row['substance_name']} {row['concentration']}" for row in cursor.fetchall()]
                substances_str = "; ".join(substances_list) if substances_list else ""

                cursor.execute('''
                    SELECT c.culture_name
                    FROM pesticide_cultures pc
                    JOIN cultures c ON pc.culture_id = c.id
                    WHERE pc.pesticide_id = ?
                ''', (pid,))
                cultures_list = [row['culture_name'] for row in cursor.fetchall()]
                cultures_str = ", ".join(cultures_list) if cultures_list else ""

                cursor.execute('''
                    SELECT d.disease_name
                    FROM pesticide_diseases pd
                    JOIN diseases d ON pd.disease_id = d.id
                    WHERE pd.pesticide_id = ?
                ''', (pid,))
                diseases_list = [row['disease_name'] for row in cursor.fetchall()]
                diseases_str = ", ".join(diseases_list) if diseases_list else ""

                data_rows.append({
                    'Название': pest['name'],
                    'Тип': pest.get('pesticide_type', ''),
                    'Действующие вещества': substances_str,
                    'Описание': pest.get('description') or '',
                    'Норма расхода': pest.get('application_rate') or '',
                    'Фасовка': pest.get('packaging') or '',
                    'Цена, руб.': pest['price'],
                    'Производитель': pest.get('manufacturer') or '',
                    'Культуры': cultures_str,
                    'Болезни': diseases_str,
                })

            df = pd.DataFrame(data_rows)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"catalog_export_{timestamp}.xlsx"

            def on_file_saved(file_path):
                try:
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Препараты', index=False)
                        worksheet = writer.sheets['Препараты']
                        for column in worksheet.columns:
                            max_length = 0
                            col_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[col_letter].width = adjusted_width
                    self._show_success_message(f"Каталог сохранён: {os.path.basename(file_path)}")
                except Exception as e:
                    self._show_error_message(f"Ошибка сохранения: {e}")

            self._save_file_dialog(
                title="Сохранить каталог",
                filters=[("Excel files", "*.xlsx")],
                default_name=default_name,
                on_success=on_file_saved
            )

        except Exception as e:
            self._show_error_message(f"Ошибка экспорта: {str(e)[:100]}")
    

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