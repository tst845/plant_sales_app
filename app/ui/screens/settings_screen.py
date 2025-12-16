from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.scrollview import ScrollView

Builder.load_string('''
<SettingsTab>:
    name: 'settings'
    text: 'Импорт/Экспорт'
    icon: 'database-export'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'
        
        MDLabel:
            text: 'Управление данными'
            halign: 'center'
            font_style: 'H5'
            size_hint_y: None
            height: self.texture_size[1]
        
        ScrollView:
            MDList:
                id: settings_list
                
<ImportExportDialog>:
    orientation: "vertical"
    spacing: "10dp"
    padding: "20dp"
    size_hint_y: None
    height: "200dp"
    
    MDLabel:
        text: root.dialog_text
        halign: "center"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: self.texture_size[1]
    
    MDBoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "10dp"
        
        MDFlatButton:
            text: "Отмена"
            on_release: root.cancel_callback()
        
        MDRaisedButton:
            text: "Продолжить"
            on_release: root.confirm_callback()
''')

class ImportExportDialog(MDBoxLayout):
    """Диалог для операций импорта/экспорта"""
    
    def __init__(self, dialog_text, confirm_callback, cancel_callback, **kwargs):
        super().__init__(**kwargs)
        self.dialog_text = dialog_text
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback

class SettingsTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        
    def on_enter(self):
        """Вызывается при переходе на вкладку"""
        self._setup_settings_list()
    
    def _setup_settings_list(self):
        """Настройка списка параметров"""
        settings_list = self.ids.settings_list
        settings_list.clear_widgets()
        
        # Секция импорта данных
        settings_list.add_widget(OneLineListItem(
            text="📥 Импорт препаратов из Excel",
            on_release=lambda x: self.show_import_dialog("препараты")
        ))
        
        settings_list.add_widget(OneLineListItem(
            text="📥 Импорт клиентов из Excel", 
            on_release=lambda x: self.show_import_dialog("клиенты")
        ))
        
        # Секция экспорта данных
        settings_list.add_widget(OneLineListItem(
            text="📤 Экспорт каталога в Excel",
            on_release=lambda x: self.show_export_dialog("каталог")
        ))
        
        settings_list.add_widget(OneLineListItem(
            text="📤 Экспорт заказов в Excel",
            on_release=lambda x: self.show_export_dialog("заказы")
        ))
        
        settings_list.add_widget(OneLineListItem(
            text="📄 Экспорт коммерческого предложения",
            on_release=lambda x: self.show_export_dialog("КП")
        ))
        
        # Секция управления БД
        settings_list.add_widget(OneLineListItem(
            text="🔄 Обновить базу данных",
            on_release=lambda x: self.update_database()
        ))
        
        settings_list.add_widget(OneLineListItem(
            text="🗑️ Очистить локальные данные",
            on_release=lambda x: self.clear_database()
        ))
        settings_list.add_widget(OneLineListItem(
            text="🔄 Обновить классы заболеваний",
            on_release=lambda x: self.update_disease_classes()
        ))
    
    def update_disease_classes(self):
        """Обновить классы заболеваний из файла"""
        try:
            # Здесь будет вызов метода из БД
            print("🔄 Обновление классов заболеваний из файла")
            self.show_message("Классы заболеваний обновлены из файла disease_classes.txt")
        except Exception as e:
            self.show_message(f"❌ Ошибка обновления: {e}")

    def show_import_dialog(self, data_type):
        """Показать диалог импорта"""
        self.dialog = MDDialog(
            title=f"Импорт {data_type}",
            type="custom",
            content_cls=ImportExportDialog(
                dialog_text=f"Функция импорта {data_type} из Excel будет реализована в следующей версии.",
                confirm_callback=lambda: self.import_data(data_type),
                cancel_callback=self.close_dialog
            ),
            size_hint=(0.8, None),
            height="250dp"
        )
        self.dialog.open()
    
    def show_export_dialog(self, data_type):
        """Показать диалог экспорта"""
        self.dialog = MDDialog(
            title=f"Экспорт {data_type}",
            type="custom", 
            content_cls=ImportExportDialog(
                dialog_text=f"Функция экспорта {data_type} в Excel будет реализована в следующей версии.",
                confirm_callback=lambda: self.export_data(data_type),
                cancel_callback=self.close_dialog
            ),
            size_hint=(0.8, None),
            height="250dp"
        )
        self.dialog.open()
    
    def import_data(self, data_type):
        """Заглушка для импорта данных"""
        print(f"📥 Импорт {data_type} из Excel")
        self.show_message(f"Импорт {data_type} выполнен успешно!")
        self.close_dialog()
    
    def export_data(self, data_type):
        """Заглушка для экспорта данных"""
        print(f"📤 Экспорт {data_type} в Excel")
        self.show_message(f"Экспорт {data_type} выполнен успешно!")
        self.close_dialog()
    
    def update_database(self):
        """Заглушка для обновления БД"""
        print("🔄 Обновление базы данных")
        self.show_message("База данных обновлена!")
    
    def clear_database(self):
        """Заглушка для очистки данных"""
        self.dialog = MDDialog(
            title="Очистка данных",
            text="Эта операция удалит все локальные данные. Продолжить?",
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda x: self.close_dialog()
                ),
                MDRaisedButton(
                    text="Очистить",
                    on_release=lambda x: self.confirm_clear()
                )
            ]
        )
        self.dialog.open()
    
    def confirm_clear(self):
        """Подтверждение очистки данных"""
        print("🗑️ Очистка локальных данных")
        self.show_message("Локальные данные очищены!")
        self.close_dialog()
    
    def show_message(self, message):
        """Показать сообщение (в будущем можно заменить на Snackbar)"""
        print(f"💬 {message}")
    
    def close_dialog(self):
        """Закрыть диалоговое окно"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
    