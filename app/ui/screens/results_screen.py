from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

Builder.load_string('''
<ResultsScreen>:
    orientation: 'vertical'
    padding: '20dp'
    spacing: '20dp'
    
    MDLabel:
        text: 'Результаты анализа'
        halign: 'center'
        font_style: 'H4'
''')

class ResultsScreen(MDBoxLayout):
    pass