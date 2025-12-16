from kivy.lang import Builder
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

Builder.load_string('''
<DiseaseDetectionScreen>:
    orientation: 'vertical'
    padding: '20dp'
    spacing: '20dp'
    
    MDLabel:
        text: 'Диагностика заболеваний'
        halign: 'center'
        font_style: 'H4'
''')

class DiseaseDetectionScreen(MDBoxLayout):
    pass