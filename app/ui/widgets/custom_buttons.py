from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp

class EditSubstancesButton(MDIconButton):
    """Кнопка для редактирования действующих веществ"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = 'flask'
        self.icon_color="red"
        self.tooltip_text = 'Редактировать ДВ'
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))

class NavigationButton(ButtonBehavior, MDBoxLayout):
    """Кнопка навигации с иконкой и текстом"""
    icon = StringProperty("")
    text = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = ("80dp", "80dp")
        self.padding = "10dp"
        self.spacing = "5dp"

class PrimaryButton(ButtonBehavior, MDBoxLayout):
    """Основная кнопка приложения"""
    text = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.height = "48dp"
        self.padding = "20dp", "10dp"