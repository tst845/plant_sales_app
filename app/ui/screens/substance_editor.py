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