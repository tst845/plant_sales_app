from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout

class ClickableImage(ButtonBehavior, Image):
    """Изображение с возможностью нажатия"""
    pass

class ImageWithCaption(MDBoxLayout):
    """Изображение с подписью"""
    pass