from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.lang import Builder
from kivy.metrics import dp

Builder.load_string('''
<SubstanceItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(50)
    padding: [dp(5), dp(5)]
    spacing: dp(5)
    
    Label:
        id: display_label
        text: root.display_text
        size_hint_x: 0.7
        halign: 'left'
        valign: 'middle'
        text_size: self.width, None
        on_touch_down: root.on_label_touch(self, args) if self.collide_point(*args.pos) else False
        
    BoxLayout:
        id: edit_container
        size_hint_x: 0.7
        orientation: 'horizontal'
        spacing: dp(5)
        opacity: 0 if not root.editing else 1
        disabled: not root.editing
        
        DropDownButton:
            id: substance_dropdown
            text: root.substance_name if root.substance_name else 'Выбрать ДВ'
            size_hint_x: 0.6
            on_release: root.show_substance_dropdown()
            
        TextInput:
            id: concentration_input
            text: root.concentration
            hint_text: 'Концентрация'
            size_hint_x: 0.4
            multiline: False
            on_text_validate: root.save_changes()
    
    BoxLayout:
        size_hint_x: 0.3
        orientation: 'horizontal'
        spacing: dp(5)
        
        IconButton:
            id: edit_btn
            icon: 'pencil' if not root.editing else 'content-save'
            size_hint_x: 0.5
            on_release: root.toggle_edit_mode()
            
        IconButton:
            id: delete_btn
            icon: 'delete'
            size_hint_x: 0.5
            on_release: root.delete_item()
''')

class DropDownButton(Button):
    pass

class IconButton(Button):
    pass

class SubstanceItem(BoxLayout):
    """Виджет строки с действующим веществом для inline-редактирования"""
    
    # Свойства
    substance_id = StringProperty('')
    substance_name = StringProperty('')
    concentration = StringProperty('')
    editing = BooleanProperty(False)
    on_save = ObjectProperty(None)
    on_delete = ObjectProperty(None)
    available_substances = ObjectProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown = None
        self.update_display_text()
    
    @property
    def display_text(self):
        """Текст для отображения в режиме просмотра"""
        if self.substance_name and self.concentration:
            return f"{self.substance_name}: {self.concentration}"
        elif self.substance_name:
            return self.substance_name
        return "Не указано"
    
    def update_display_text(self):
        """Обновить текст отображения"""
        self.ids.display_label.text = self.display_text
    
    def on_label_touch(self, instance, touch):
        """Обработка касания метки для перехода в режим редактирования"""
        if touch.is_double_tap and not self.editing:
            self.editing = True
            return True
    
    def toggle_edit_mode(self):
        """Переключение режима редактирования"""
        if self.editing:
            self.save_changes()
        else:
            self.editing = True
    
    def save_changes(self):
        """Сохранение изменений"""
        if self.editing:
            # Обновляем концентрацию
            self.concentration = self.ids.concentration_input.text
            
            # Если выбранное вещество из dropdown
            if hasattr(self, 'selected_substance'):
                self.substance_name = self.selected_substance['name']
                self.substance_id = self.selected_substance['id']
            
            self.update_display_text()
            self.editing = False
            
            if self.on_save:
                self.on_save(self)
    
    def show_substance_dropdown(self):
        """Показать dropdown с доступными веществами"""
        if not self.available_substances:
            return
        
        self.dropdown = DropDown()
        
        for substance in self.available_substances:
            btn = Button(
                text=substance['name'],
                size_hint_y=None,
                height=dp(40)
            )
            btn.bind(on_release=lambda btn, s=substance: self.select_substance(s))
            self.dropdown.add_widget(btn)
        
        self.dropdown.open(self.ids.substance_dropdown)
    
    def select_substance(self, substance):
        """Выбор вещества из dropdown"""
        self.selected_substance = substance
        self.ids.substance_dropdown.text = substance['name']
        if self.dropdown:
            self.dropdown.dismiss()
    
    def delete_item(self):
        """Удаление строки"""
        if self.on_delete:
            self.on_delete(self)