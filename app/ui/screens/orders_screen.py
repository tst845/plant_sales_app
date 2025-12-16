from kivy.lang import Builder
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

Builder.load_string('''
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

class OrdersTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)