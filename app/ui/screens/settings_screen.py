from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem, ThreeLineListItem
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivymd.app import MDApp
import pandas as pd
import os
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.utils import platform

if platform == 'android':
    from plyer import filechooser
else:
    import tkinter.filedialog as filedialog
    import tkinter as Tk


Builder.load_string('''
<SettingsTab>:
    name: 'settings'
    text: 'Импорт/Экспорт'
    icon: 'database-export'

    MDBoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'

        # Кастомная шапка
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            padding: [dp(10), 0, dp(10), 0]
            spacing: dp(10)
            md_bg_color: [0.95, 0.95, 0.95, 1]

            MDLabel:
                text: "Управление данными"
                font_style: "H6"
                size_hint_x: 1
                size_hint_y: 1
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                halign: "center"
                valign: "middle"

            MDIconButton:
                icon: "help-circle-outline"
                theme_icon_color: "Custom"
                icon_color: "green"
                size_hint: None, None
                size: dp(32), dp(32)
                pos_hint: {"center_y": 0.5}
                on_release: root.show_help()

        # Список с прокруткой (как раньше)
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
    dialog_text = StringProperty("")
    def __init__(self, dialog_text, confirm_callback, cancel_callback, **kwargs):
        super().__init__(**kwargs)
        self.dialog_text = dialog_text
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback

class SettingsTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.skipped_dialog = None
        
    def on_enter(self):
        """Вызывается при переходе на вкладку"""
        self._setup_settings_list()
    
    def show_help(self):
        """Показать справочную информацию по модулю управления данными"""
        help_text = (
            "Импорт препаратов из Excel:\n"
            "  • Добавляет новые препараты из прайс-листа. Дубликаты по названию пропускаются.\n\n"
            "Обновить препараты из Excel:\n"
            "  • Обновляет цены, упаковку, нормы расхода и действующие вещества у существующих препаратов. "
            "Добавляет новые, если их нет в базе.\n\n"
            "Импорт описаний препаратов из Excel:\n"
            "  • Заполняет описания, культуры и болезни для уже имеющихся препаратов.\n\n"
            "Экспорт каталога в Excel:\n"
            "  • Сохраняет весь каталог в файл Excel с полной информацией.\n\n"
            "Очистить БД:\n"
            "  • Удаляет все данные о препаратах, клиентах и заказах. Справочники (культуры, болезни, "
            "действующие вещества) также очищаются.\n\n"
            "Шаблоны импорта:\n"
            "  • «Скачать шаблон импорта препаратов» – Excel-файл с колонками:\n"
            "    Препараты, Состав, Производитель, Упаковка, Норма расхода, кг(л)/га, Цена за ед. (с НДС) в руб.\n"
            "  • «Скачать шаблон импорта описаний» – Excel-файл с колонками:\n"
            "    Название, Культуры, Болезни, Описание.\n\n"
            "Порядок обновления каталога:\n"
            "  1. Импортируйте препараты (или обновите их) из прайс-листа.\n"
            "  2. При необходимости импортируйте описания.\n"
            "  3. Используйте экспорт для создания резервной копии."
        )

        content = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(490),
            spacing=dp(8),
            padding=dp(17),
            md_bg_color=(0.96, 0.96, 0.96, 1),
        )

        label = MDLabel(
            text=help_text,
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            size_hint_y=None,
            halign="left",
            valign="top",
            font_style="Caption",
        )
        label.bind(texture_size=label.setter('size'))

        scroll = ScrollView(size_hint_y=1, do_scroll_x=False)
        scroll.add_widget(label)
        content.add_widget(scroll)

        dialog = MDDialog(
            title="Справочная информация",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="Закрыть",
                    theme_text_color="Custom",
                    text_color="white",
                    md_bg_color="green",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
            size_hint=(0.95, 0.85)
        )

        def set_title_color(dialog_inst, dt):
            for child in dialog_inst.children:
                if hasattr(child, 'title') and hasattr(child, 'text_color'):
                    child.theme_text_color = "Custom"
                    child.text_color = (0, 0.7, 0, 1)
                    break
        Clock.schedule_once(lambda dt: set_title_color(dialog, dt), 0.1)

        dialog.open()

    def _open_file_dialog(self, title, filters, on_success):
        """Открывает диалог выбора файла. on_success(file_path) будет вызван при выборе."""
        if platform == 'android':
            android_filters = [f[1] for f in filters]
            filechooser.open_file(title=title, filters=android_filters, on_selection=lambda sel: self._on_file_selected(sel, on_success))
        else:
            root = Tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(title=title, filetypes=filters)
            root.destroy()
            if file_path:
                on_success(file_path)

    def _save_file_dialog(self, title, filters, default_name, on_success):
        """Открывает диалог сохранения файла. on_success(file_path) будет вызван при выборе."""
        if platform == 'android':
            android_filters = [f[1] for f in filters]  
            filechooser.save_file(title=title, filters=android_filters, filename=default_name,
                                on_selection=lambda sel: self._on_file_selected(sel, on_success))
        else:
            root = Tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.asksaveasfilename(title=title, defaultextension=".xlsx",
                                                    filetypes=filters, initialfile=default_name)
            root.destroy()
            if file_path:
                on_success(file_path)

    def _on_file_selected(self, selection, callback):
        """Вспомогательный метод для обработки результата Plyer filechooser."""
        if selection and len(selection) > 0:
            callback(selection[0])
        # else пользователь отменил выбор – ничего не делаем

    def _setup_settings_list(self):
        """Настройка списка параметров"""
        settings_list = self.ids.settings_list
        settings_list.clear_widgets()
        
        # Секция импорта данных
        settings_list.add_widget(OneLineListItem(
            text=" Импорт препаратов из Excel",
            on_release=lambda x: self.show_import_dialog("препараты")
        ))
        settings_list.add_widget(OneLineListItem(
            text=" Обновить препараты из Excel",
            on_release=lambda x: self.start_update_pesticides()
        ))
        settings_list.add_widget(OneLineListItem(
            text=" Импорт описаний препаратов из Excel",
            on_release=lambda x: self.start_import_descriptions()
        ))
  
        # Секция экспорта данных
        settings_list.add_widget(OneLineListItem(
            text=" Экспорт каталога в Excel",
            on_release=lambda x: self.show_export_dialog("каталог")
        ))
      
        settings_list.add_widget(OneLineListItem(
            text=" Очистить БД",
            on_release=lambda x: self.confirm_clear_except_models()
        ))
 
        # Шаблоны
        settings_list.add_widget(OneLineListItem(
            text=" Скачать шаблон импорта препаратов",
            on_release=lambda x: self.show_template_dialog('pesticides')
        ))
        settings_list.add_widget(OneLineListItem(
            text=" Скачать шаблон импорта описаний",
            on_release=lambda x: self.show_template_dialog('descriptions')
        ))

    def start_import_descriptions(self):
        def on_file_selected(file_path):
            self.current_import_file = file_path
            try:
                xl = pd.ExcelFile(file_path)
                sheets = xl.sheet_names
                self.show_description_sheet_selection_dialog(sheets)
            except Exception as e:
                self.show_message(f"Ошибка чтения файла: {e}")

        self._open_file_dialog(
            title="Выберите Excel-файл с описаниями",
            filters=[("Excel files", "*.xlsx")],
            on_success=on_file_selected
        )

    def show_description_sheet_selection_dialog(self, sheets):
        """Диалог с чекбоксами для выбора листов описаний"""
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content.height = len(sheets) * 50 + 100
        scroll = ScrollView()
        list_widget = MDList()
        checkboxes = {}
        for sheet in sheets:
            if sheet.startswith('_'):
                continue
            box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=48, padding=[10,0,10,0])
            chk = MDCheckbox(size_hint_x=None, width=48)
            lbl = MDLabel(text=sheet, size_hint_x=1)
            box.add_widget(chk)
            box.add_widget(lbl)
            list_widget.add_widget(box)
            checkboxes[sheet] = chk
        scroll.add_widget(list_widget)
        content.add_widget(scroll)
        btn_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=10, padding=10)
       
        btn_cancel = MDFlatButton(
            text="Отмена",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.close_dialog()
        )
        btn_ok = MDRaisedButton(
            text="Далее",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.process_selected_description_sheets(checkboxes)
        )
        
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_ok)
        content.add_widget(btn_box)
        self.dialog = MDDialog(title="Выберите листы с описаниями", type="custom", content_cls=content,
                            size_hint=(0.9, 0.8), auto_dismiss=False)
        self.dialog.open()

    def process_selected_description_sheets(self, checkboxes):
        """Обработка выбранных листов и запуск парсинга"""
        selected = [sheet for sheet, chk in checkboxes.items() if chk.active]
        if not selected:
            self.show_message("Ни одного листа не выбрано")
            return
        self.dialog.dismiss()
        self._import_descriptions(selected)

    def _import_descriptions(self, selected_sheets):
        """Парсинг выбранных листов описаний, сохранение в БД (в транзакции)"""
        try:
            app = MDApp.get_running_app()
            db = app.db
            cursor = db.connection.cursor()
            cursor.execute("BEGIN TRANSACTION")

            total_updated = 0
            not_found_list = []   # (название, причина)

            for sheet_name in selected_sheets:
                df = pd.read_excel(self.current_import_file, sheet_name=sheet_name, header=0)
                required = ['Название', 'Культуры', 'Болезни', 'Описание']
                if not all(col in df.columns for col in required):
                    missing = [col for col in required if col not in df.columns]
                    found = [col for col in df.columns if col in required]
                    not_found_list.append((
                        f"Лист '{sheet_name}'",
                        f"Отсутствуют колонки: {', '.join(missing)}.\nНайдены: {', '.join(found) if found else 'нет'}" ))
                    continue

                for _, row in df.iterrows():
                    name = str(row['Название']).strip()
                    if not name:
                        continue
                    cursor.execute("SELECT id, description FROM pesticides WHERE name = ?", (name,))
                    res = cursor.fetchone()
                    if not res:
                        not_found_list.append((name, "Препарат не найден в БД"))
                        continue

                    pesticide_id = res['id']
                    old_description = res['description'] or ""

                    new_description = str(row['Описание']).strip() if pd.notna(row['Описание']) else ""
                    cultures_str = str(row['Культуры']).strip() if pd.notna(row['Культуры']) else ""
                    diseases_str = str(row['Болезни']).strip() if pd.notna(row['Болезни']) else ""

                    has_changes = False

                    if new_description != old_description:
                        cursor.execute("UPDATE pesticides SET description = ? WHERE id = ?", (new_description, pesticide_id))
                        has_changes = True

                    if cultures_str:
                        cursor.execute("DELETE FROM pesticide_cultures WHERE pesticide_id = ?", (pesticide_id,))
                        culture_list = [c.strip() for c in cultures_str.split(',') if c.strip()]
                        for cult_name in culture_list:
                            culture_id = db.get_or_create_culture(cult_name, cursor=cursor)
                            cursor.execute("INSERT OR IGNORE INTO pesticide_cultures (pesticide_id, culture_id) VALUES (?, ?)",
                                        (pesticide_id, culture_id))
                        has_changes = True

                    if diseases_str:
                        cursor.execute("DELETE FROM pesticide_diseases WHERE pesticide_id = ?", (pesticide_id,))
                        disease_list = [d.strip() for d in diseases_str.split(',') if d.strip()]
                        for dis_name in disease_list:
                            disease_id = db.get_or_create_disease(dis_name, cursor=cursor)
                            cursor.execute("INSERT OR IGNORE INTO pesticide_diseases (pesticide_id, disease_id) VALUES (?, ?)",
                                        (pesticide_id, disease_id))
                        has_changes = True

                    if has_changes:
                        total_updated += 1


            self.current_import_stats = {
                'cursor': cursor,
                'updated': total_updated,
                'not_found': not_found_list,
            }
            self.show_description_import_report_dialog()

        except Exception as e:
            if 'cursor' in locals():
                cursor.execute("ROLLBACK")
            self.show_message(f"Ошибка импорта описаний: {e}")
            import traceback
            traceback.print_exc()
    
    def show_description_import_report_dialog(self):
        """Диалог с отчётом импорта описаний"""
        stats = self.current_import_stats
        not_found = stats.get('not_found', [])
        report_text = f"Обновлено препаратов: {stats['updated']}\n"
        report_text += f"Не найдено: {len(not_found)}\n"

        if not_found:
            report_text += "\nСписок ненайденных препаратов будет доступен по кнопке «Подробнее»."

        label = MDLabel(
            text=report_text,
            size_hint_y=None,
            halign='left',
            valign='top',
            padding=(10, 10)
        )
        label.bind(texture_size=label.setter('size'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(label)

        btn_cancel = MDFlatButton(
            text="Отмена",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.cancel_import()
        )
        btn_skipped = MDFlatButton(
            text="Подробнее",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.show_description_skipped_dialog()
        )
        btn_confirm = MDRaisedButton(
            text="Принять",  # или "Обновить"
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.confirm_description_import()
        )

        btn_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=10, padding=[10,5,10,5])
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_skipped)
        btn_box.add_widget(btn_confirm)

        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None,
                            height=dp(250) + btn_box.height)
        content.add_widget(scroll)
        content.add_widget(btn_box)

        dialog = MDDialog(
            title="Импорт описаний",
            type="custom",
            content_cls=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        dialog.open()
        self.dialog = dialog

    def confirm_description_import(self):
        """Подтверждение импорта описаний: фиксация транзакции и обновление каталога"""
        self.close_skipped_dialog()
        if not hasattr(self, 'current_import_stats') or not self.current_import_stats:
            self.close_dialog()
            return
        stats = self.current_import_stats
        cursor = stats.get('cursor')
        if cursor:
            cursor.connection.commit()
        self.close_dialog()
        self.show_message(f"Описания импортированы. Обновлено: {stats['updated']}, не найдено: {len(stats.get('not_found', []))}")

        # Обновляем каталог
        app = MDApp.get_running_app()
        if app.screen_manager:
            for screen in app.screen_manager.screens:
                if screen.name == 'catalog' and hasattr(screen, '_load_pesticides'):
                    screen._load_pesticides()
                    break
        self.current_import_stats = None

    def show_description_skipped_dialog(self):
        stats = self.current_import_stats
        if not stats:
            return
        not_found = stats.get('not_found', [])
        if not not_found:
            self.show_message("Нет пропущенных записей")
            return

        if self.skipped_dialog:
            self.skipped_dialog.dismiss()
            self.skipped_dialog = None

        items_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=6
        )
        items_box.bind(minimum_height=items_box.setter('height'))

        for name, reason in not_found:
            item_box = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                adaptive_height=True,
                spacing=2,
                padding=[5, 5, 5, 5]
            )
            lbl_name = MDLabel(
                text=name,
                font_style='Subtitle1',
                theme_text_color='Primary',
                size_hint_y=None,
                halign='left'
            )
            lbl_reason = MDLabel(
                text=reason,
                font_style='Body2',
                theme_text_color='Secondary',
                size_hint_y=None,
                halign='left'
            )
            lbl_name.bind(texture_size=lbl_name.setter('size'))
            lbl_reason.bind(texture_size=lbl_reason.setter('size'))
            item_box.add_widget(lbl_name)
            item_box.add_widget(lbl_reason)
            items_box.add_widget(item_box)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(items_box)

        btn_close = MDFlatButton(
            text="Закрыть",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
        )
        btn_close.bind(on_release=lambda instance: self.close_skipped_dialog())
        content = MDBoxLayout(orientation='vertical', spacing=6, size_hint_y=None, height=dp(300))
        content.add_widget(scroll)
        content.add_widget(btn_close)

        self.skipped_dialog = MDDialog(
            title="Не найденные препараты",
            type="custom",
            content_cls=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=True
        )
        self.skipped_dialog.open()

    def update_disease_classes(self):
        """Обновить классы заболеваний из файла"""
        try:
            # Здесь будет вызов метода из БД
            print(" Обновление классов заболеваний из файла")
            self.show_message("Классы заболеваний обновлены из файла disease_classes.txt")
        except Exception as e:
            self.show_message(f"❌ Ошибка обновления: {e}")

    def clear_database_except_models(self):
        self.close_dialog()  # закрываем диалог подтверждения
        app = MDApp.get_running_app()
        cursor = app.db.connection.cursor()
        tables = [
            'pesticides', 'pesticide_types', 'active_substances', 'pesticide_active_substances',
            'pesticide_cultures', 'pesticide_diseases', 'clients', 'orders', 'order_items',
            'client_cultures', 'cultures', 'diseases'
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        app.db.connection.commit()

        self.show_message("База данных очищена (классы болезней и видов сохранены).")
        self.show_info_dialog("Очистка БД", "База данных очищена (классы болезней и видов сохранены).")

    

    def show_import_dialog(self, data_type):
        if data_type == "препараты":
            self.start_import_pesticides()
        else:
            # заглушка для клиентов
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
    
    def start_import_pesticides(self):
        def on_file_selected(file_path):
            self.current_import_file = file_path
            try:
                xl = pd.ExcelFile(file_path)
                sheets = xl.sheet_names
                self.show_sheet_selection_dialog(sheets)
            except Exception as e:
                self.show_message(f"Ошибка чтения файла: {e}")

        self._open_file_dialog(
            title="Выберите Excel-файл с прайс-листом",
            filters=[("Excel files", "*.xlsx")],
            on_success=on_file_selected
        )

    
    def show_sheet_selection_dialog(self, sheets):
            """Диалог с чекбоксами для выбора листов"""
            content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
            content.height = len(sheets) * 50 + 100
            scroll = ScrollView()
            list_widget = MDList()
            checkboxes = {}
            for sheet in sheets:
                # Игнорируем служебные листы (например, если название начинается с '_')
                if sheet.startswith('_'):
                    continue
                box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=48, padding=[10,0,10,0])
                chk = MDCheckbox(size_hint_x=None, width=48)
                lbl = MDLabel(text=sheet, size_hint_x=1)
                box.add_widget(chk)
                box.add_widget(lbl)
                list_widget.add_widget(box)
                checkboxes[sheet] = chk
            scroll.add_widget(list_widget)
            content.add_widget(scroll)
            # Кнопки
            btn_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=10, padding=10)
            
            btn_cancel = MDFlatButton(
                text="Отмена",
                theme_text_color="Custom",
                text_color="white",
                md_bg_color="green",
                on_release=lambda x: self.close_dialog()
            )
            btn_ok = MDRaisedButton(
                text="Далее",
                theme_text_color="Custom",
                text_color="white",
                md_bg_color="green",
                on_release=lambda x: self.process_selected_sheets(checkboxes)
            )
 
            # btn_ok = MDRaisedButton(text="Далее", 
            #                         on_release=lambda x: self.process_selected_sheets(checkboxes))
            btn_box.add_widget(btn_cancel)
            btn_box.add_widget(btn_ok)
            content.add_widget(btn_box)
            self.dialog = MDDialog(title="Выберите листы для импорта", type="custom", content_cls=content,
                                size_hint=(0.9, 0.8), auto_dismiss=False)
            self.dialog.open()

    def process_selected_sheets(self, checkboxes):
        """Сбор выбранных листов, парсинг с определением типа по строкам-разделителям"""
        selected = [sheet for sheet, chk in checkboxes.items() if chk.active]
        if not selected:
            self.show_message("Ни одного листа не выбрано")
            return
        self.dialog.dismiss()
        self.skipped_items = []
        try:
            xl = pd.ExcelFile(self.current_import_file)
            db = MDApp.get_running_app().db
            cursor = db.connection.cursor()
            report_lines = []
            total_inserted = 0
            total_skipped = 0
            total_duplicates = 0
            processed_sheets = 0
            cursor.execute("BEGIN TRANSACTION")

            # Словарь для определения типов по ключевым словам
            type_variants = {
                "ГЕРБИЦИДЫ": "Гербициды",
                "ГЕРБЕЦИДЫ": "Гербициды",
                "ИНСЕКТИЦИДЫ": "Инсектициды",
                "ФУНГИЦИДЫ": "Фунгициды",
                "ДЕСИКАНТЫ": "Десиканты",
                "ПРОТРАВИТЕЛИ": "Протравители",
                "ФУМИГАНТЫ": "Фумиганты",
                "СПЕЦПРЕПАРАТЫ": "Спецпрепараты",
                "РОДЕНТИЦИДЫ": "Родентициды"
            }

            for sheet_name in selected:
                df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
                if df.empty:
                    continue

                # 1. Находим строку с заголовками (ищем "Препараты")
                header_row = None
                for idx, row in df.iterrows():
                    first_cell = str(row.iloc[0]).strip()
                    if first_cell == "№ п/п" or first_cell == "Препараты" or "препараты" in first_cell.lower():
                        header_row = idx
                        break
                if header_row is None:
                    report_lines.append(f"Лист '{sheet_name}': не найден заголовок, пропущен")
                    continue

                # 2. Получаем заголовки и обрезаем DataFrame до строк после заголовка
                df.columns = df.iloc[header_row].astype(str).str.strip()
                data_df = df.iloc[header_row + 1:].reset_index(drop=True)
                # print(f"DEBUG: лист '{sheet_name}', строк данных: {len(data_df)}")
                # Необходимые колонки
                required = ['Препараты', 'Состав', 'Производитель', 'Упаковка',
                            'Норма расхода, кг(л)/га', 'Цена за ед. (с НДС) в руб.']

                # Проверяем наличие колонок (если нет – пробуем найти альтернативные названия)
                if not all(col in df.columns for col in required):
                    missing = [col for col in required if col not in df.columns]
                    found = [col for col in df.columns if col in required]
                    report_lines.append(
                        f"Лист '{sheet_name}': не найдены необходимые колонки.\n"
                        f"   Ожидались: {', '.join(required)}\n"
                        f"   Найдены: {', '.join(found) if found else 'нет'}\n"
                        f"   Отсутствуют: {', '.join(missing)}"
                    )
                    continue

                sheet_inserted = 0
                sheet_skipped = 0
                sheet_duplicates = 0

                # 3. Идём по строкам данных, отслеживая текущий тип
                current_type = None
                for idx, row in data_df.iterrows():
                    first_cell = str(row.iloc[0]).strip().upper()
                    # Проверяем, является ли строка разделителем (типом)
                    if first_cell in type_variants:
                        current_type = type_variants[first_cell]
                        continue  # пропускаем строку-разделитель

                    # Пропускаем пустые строки
                    if pd.isna(row['Препараты']) or str(row['Препараты']).strip() == "":
                        continue

                    name = str(row['Препараты']).strip()
                    composition = str(row['Состав']).strip() if pd.notna(row['Состав']) else ""
                    manufacturer = str(row['Производитель']).strip() if pd.notna(row['Производитель']) else ""
                    packaging = str(row['Упаковка']).strip() if pd.notna(row['Упаковка']) else ""
                    rate = str(row['Норма расхода, кг(л)/га']).strip() if pd.notna(row['Норма расхода, кг(л)/га']) else ""
                    price_str = str(row['Цена за ед. (с НДС) в руб.']).strip() if pd.notna(row['Цена за ед. (с НДС) в руб.']) else ""
                    try:
                        price = float(price_str.replace(',', '.'))
                    except:
                        sheet_skipped += 1
                        self.skipped_items.append((sheet_name, name, "Неверная цена (не число или 'по запросу')"))
                        continue

                    # Если тип не определён, используем название листа как fallback
                    if not current_type:
                        ptype = type_variants.get(sheet_name.strip().upper(), sheet_name.capitalize())
                    else:
                        ptype = current_type

                    # Вставляем тип, если его нет
                    cursor.execute("SELECT id FROM pesticide_types WHERE type_name = ?", (ptype,))
                    res = cursor.fetchone()
                    if not res:
                        cursor.execute("INSERT INTO pesticide_types (type_name) VALUES (?)", (ptype,))
                        type_id = cursor.lastrowid
                    else:
                        type_id = res[0]

                    # Проверка дубликата по имени
                    cursor.execute("SELECT id FROM pesticides WHERE name = ?", (name,))
                    if cursor.fetchone():
                        # print(f"DEBUG: дубликат (импорт): '{name}' уже существует в БД или был добавлен ранее в этой транзакции")
                        sheet_duplicates += 1
                        self.skipped_items.append((sheet_name, name, "Дубликат в файле"))
                        continue

                    # Вставляем препарат
                    cursor.execute('''
                        INSERT INTO pesticides (name, description, application_rate, packaging, price, manufacturer, pesticide_type_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (name, "", rate, packaging, price, manufacturer, type_id))
                    pesticide_id = cursor.lastrowid

                    # Обработка действующих веществ
                    substances = self._parse_substances(composition)
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
                        cursor.execute("SELECT 1 FROM pesticide_active_substances WHERE pesticide_id = ? AND substance_id = ?", (pesticide_id, substance_id))
                        if not cursor.fetchone():
                            cursor.execute('''
                                INSERT INTO pesticide_active_substances (pesticide_id, substance_id, concentration)
                                VALUES (?, ?, ?)
                            ''', (pesticide_id, substance_id, concentration))

                    sheet_inserted += 1

                total_inserted += sheet_inserted
                total_skipped += sheet_skipped
                total_duplicates += sheet_duplicates
                processed_sheets += 1
                report_lines.append(f"Лист '{sheet_name}': добавлено {sheet_inserted}, пропущено (цена) {sheet_skipped}, дубликатов {sheet_duplicates}")

            self.current_import_stats = {
                'report': report_lines,
                'inserted': total_inserted,
                'skipped': total_skipped,
                'duplicates': total_duplicates,
                'sheets': processed_sheets,
                'cursor': cursor
            }
            self.show_import_report_dialog()
        except Exception as e:
            if 'cursor' in locals():
                cursor.execute("ROLLBACK")
            self.show_message(f"Ошибка при парсинге: {e}")
            import traceback
            traceback.print_exc()

    def show_import_report_dialog(self):
        """Диалог с отчётом и кнопками подтверждения/отмены"""
        stats = self.current_import_stats
        report_text = f"Обработано листов: {stats['sheets']}\n"
        report_text += f"Добавлено препаратов: {stats['inserted']}\n"
        report_text += f"Пропущено: {stats['skipped']}\n"
        report_text += f"Дубликатов: {stats['duplicates']}\n\n"
        if stats.get('report'):
            report_text += "\nДетали по листам:\n" + "\n".join(stats['report'])
        # Создаём MDLabel с возможностью прокрутки
        label = MDLabel(
            text=report_text,
            size_hint_y=None,
            halign='left',
            valign='top',
            padding=(10, 10)
        )
        label.bind(texture_size=label.setter('size'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(label)
        # Кнопки
     
        btn_cancel = MDFlatButton(
            text="Отмена",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.cancel_import()
        )
        btn_skipped = MDFlatButton(
            text="Подробнее",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.show_skipped_dialog()
        )
        btn_confirm = MDRaisedButton(
            text="Принять",  # или "Обновить"
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.confirm_import()
        )

        # Горизонтальный контейнер для кнопок
        btn_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=48,
            spacing=10,
            padding=[10, 5, 10, 5]
        )
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_skipped)
        btn_box.add_widget(btn_confirm)
        # Основной контейнер
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            # height=scroll.height + btn_box.height + 20
            height=dp(150)
        )
        content.add_widget(scroll)
        content.add_widget(btn_box)
        # Диалог с фиксированным размером
        dialog = MDDialog(
            title="Результат импорта",
            type="custom",
            content_cls=content,
            size_hint=(0.9, 0.9),
            auto_dismiss=False
        )
        dialog.open()
        self.dialog = dialog

    def confirm_import(self):
        """Подтверждение импорта/обновления: фиксируем транзакцию и обновляем каталог"""
        self.close_skipped_dialog()
        if not hasattr(self, 'current_import_stats') or not self.current_import_stats:
            self.close_dialog()
            return
        stats = self.current_import_stats
        cursor = stats.get('cursor')
        if cursor:
            cursor.connection.commit()
        self.close_dialog()

        # Формируем сообщение в зависимости от типа операции
        if 'inserted' in stats:
            # Режим импорта
            count = stats['inserted']
            self.show_message(f"Импорт завершён. Добавлено {count} препаратов.")
        else:
            # Режим обновления
            new_count = stats.get('new', 0)
            updated_count = stats.get('updated', 0)
            unchanged_count = stats.get('unchanged', 0)
            self.show_message(f"Обновление завершено. Новых: {new_count}, обновлено: {updated_count}, без изменений: {unchanged_count}")

        # Обновляем каталог
        app = MDApp.get_running_app()
        if app.screen_manager:
            for screen in app.screen_manager.screens:
                if screen.name == 'catalog':
                    if hasattr(screen, '_load_pesticides'):
                        screen._load_pesticides()
                    break
        self.current_import_stats = None

    def show_skipped_dialog(self):
        if not self.skipped_items:
            self.show_message("Нет пропущенных записей")
            return

        if self.skipped_dialog:
            self.skipped_dialog.dismiss()
            self.skipped_dialog = None

        items_box = MDBoxLayout(orientation='vertical', size_hint_y=None, spacing=6)
        items_box.bind(minimum_height=items_box.setter('height'))

        for sheet, name, reason in self.skipped_items:
            item_box = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                adaptive_height=True,
                spacing=2,
                padding=[5, 5, 5, 5]
            )
            lbl_name = MDLabel(
                text=name,
                font_style='Subtitle1',
                theme_text_color='Primary',
                size_hint_y=None,
                halign='left'
            )
            lbl_sheet = MDLabel(
                text=f"Лист: {sheet}",
                font_style='Body2',
                theme_text_color='Secondary',
                size_hint_y=None,
                halign='left'
            )
            lbl_reason = MDLabel(
                text=reason,
                font_style='Body2',
                theme_text_color='Secondary',
                size_hint_y=None,
                halign='left'
            )
            lbl_name.bind(texture_size=lbl_name.setter('size'))
            lbl_sheet.bind(texture_size=lbl_sheet.setter('size'))
            lbl_reason.bind(texture_size=lbl_reason.setter('size'))
            item_box.add_widget(lbl_name)
            item_box.add_widget(lbl_sheet)
            item_box.add_widget(lbl_reason)
            items_box.add_widget(item_box)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(items_box)

        btn_close = MDFlatButton(
            text="Закрыть",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
        )
        btn_close.bind(on_release=lambda instance: self.close_skipped_dialog())
        content = MDBoxLayout(orientation='vertical', spacing=6, size_hint_y=None, height=dp(300))
        content.add_widget(scroll)
        content.add_widget(btn_close)

        self.skipped_dialog = MDDialog(
            title="Пропущенные и дублирующиеся записи",
            type="custom",
            content_cls=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=True
        )
        self.skipped_dialog.open()

    def close_skipped_dialog(self):
        if self.skipped_dialog:
            self.skipped_dialog.dismiss()
            self.skipped_dialog = None

    def start_update_pesticides(self):
        def on_file_selected(file_path):
            self.current_import_file = file_path
            try:
                xl = pd.ExcelFile(file_path)
                sheets = xl.sheet_names
                self.show_sheet_selection_dialog_for_update(sheets)
            except Exception as e:
                self.show_message(f"Ошибка чтения файла: {e}")

        self._open_file_dialog(
            title="Выберите Excel-файл с прайс-листом для обновления",
            filters=[("Excel files", "*.xlsx")],
            on_success=on_file_selected
        )

    def show_sheet_selection_dialog_for_update(self, sheets):
        """Диалог выбора листов для обновления (такой же, как для импорта)"""
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content.height = len(sheets) * 50 + 100
        scroll = ScrollView()
        list_widget = MDList()
        checkboxes = {}
        for sheet in sheets:
            if sheet.startswith('_'):
                continue
            box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=48, padding=[10,0,10,0])
            chk = MDCheckbox(size_hint_x=None, width=48)
            lbl = MDLabel(text=sheet, size_hint_x=1)
            box.add_widget(chk)
            box.add_widget(lbl)
            list_widget.add_widget(box)
            checkboxes[sheet] = chk
        scroll.add_widget(list_widget)
        content.add_widget(scroll)
        btn_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=10, padding=10)
                
        btn_cancel = MDFlatButton(
            text="Отмена",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.close_dialog()
        )
        btn_ok = MDRaisedButton(
            text="Далее",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.process_selected_sheets_for_update(checkboxes)
        )
        
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_ok)
        content.add_widget(btn_box)
        self.dialog = MDDialog(title="Выберите листы для обновления", type="custom", content_cls=content,
                            size_hint=(0.9, 0.8), auto_dismiss=False)
        self.dialog.open()

    def process_selected_sheets_for_update(self, checkboxes):
        selected = [sheet for sheet, chk in checkboxes.items() if chk.active]
        if not selected:
            self.show_message("Ни одного листа не выбрано")
            return
        self.dialog.dismiss()
        self.skipped_items = []
        try:
            xl = pd.ExcelFile(self.current_import_file)
            db = MDApp.get_running_app().db
            cursor = db.connection.cursor()
            cursor.execute("BEGIN TRANSACTION")

            # Загружаем существующие препараты
            cursor.execute("SELECT id, name, price, application_rate, packaging, manufacturer, pesticide_type_id, description FROM pesticides")
            existing = {}
            for row in cursor.fetchall():
                existing[row['name']] = {
                    'id': row['id'],
                    'price': row['price'],
                    'application_rate': row['application_rate'],
                    'packaging': row['packaging'],
                    'manufacturer': row['manufacturer'],
                    'pesticide_type_id': row['pesticide_type_id'],
                    'description': row['description']
                }
            cursor.execute("SELECT id, type_name FROM pesticide_types")
            type_map = {row['type_name']: row['id'] for row in cursor.fetchall()}

            type_variants = {
                "ГЕРБИЦИДЫ": "Гербициды",
                "ГЕРБЕЦИДЫ": "Гербициды",
                "ИНСЕКТИЦИДЫ": "Инсектициды",
                "ФУНГИЦИДЫ": "Фунгициды",
                "ДЕСИКАНТЫ": "Десиканты",
                "ПРОТРАВИТЕЛИ": "Протравители",
                "ФУМИГАНТЫ": "Фумиганты",
                "СПЕЦПРЕПАРАТЫ": "Спецпрепараты",
                "РОДЕНТИЦИДЫ": "Родентициды"
            }

            report_lines = []
            total_new = 0
            total_updated = 0
            total_unchanged = 0
            total_skipped = 0
            processed_sheets = 0

            for sheet_name in selected:
                df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
                if df.empty:
                    continue

                # Находим строку с заголовками
                header_row = None
                for idx, row in df.iterrows():
                    first_cell = str(row.iloc[0]).strip()
                    if first_cell in ("№ п/п", "Препараты") or "препараты" in first_cell.lower():
                        header_row = idx
                        break
                if header_row is None:
                    report_lines.append(f"Лист '{sheet_name}': не найден заголовок, пропущен")
                    continue

                df.columns = df.iloc[header_row].astype(str).str.strip()
                data_df = df.iloc[header_row + 1:].reset_index(drop=True)
                # print(f"DEBUG: лист '{sheet_name}', строк данных: {len(data_df)}")
                required = ['Препараты', 'Состав', 'Производитель', 'Упаковка',
                            'Норма расхода, кг(л)/га', 'Цена за ед. (с НДС) в руб.']
                if not all(col in data_df.columns for col in required):
                    missing = [col for col in required if col not in data_df.columns]
                    found = [col for col in data_df.columns if col in required]
                    report_lines.append(
                        f"Лист '{sheet_name}': не найдены необходимые колонки.\n"
                        f"   Ожидались: {', '.join(required)}\n"
                        f"   Найдены: {', '.join(found) if found else 'нет'}\n"
                        f"   Отсутствуют: {', '.join(missing)}"
                    )
                    continue

                sheet_new = 0
                sheet_updated = 0
                sheet_unchanged = 0
                sheet_skipped = 0
                current_type = None

                for _, row in data_df.iterrows():
                    first_cell = str(row.iloc[0]).strip().upper()
                    # Проверяем, является ли строка разделителем
                    if first_cell in type_variants:
                        current_type = type_variants[first_cell]
                        continue

                    # Пропускаем пустые строки
                    if pd.isna(row['Препараты']) or str(row['Препараты']).strip() == "":
                        continue

                    name = str(row['Препараты']).strip()
                    composition = str(row['Состав']).strip() if pd.notna(row['Состав']) else ""
                    manufacturer = str(row['Производитель']).strip() if pd.notna(row['Производитель']) else ""
                    packaging = str(row['Упаковка']).strip() if pd.notna(row['Упаковка']) else ""
                    rate = str(row['Норма расхода, кг(л)/га']).strip() if pd.notna(row['Норма расхода, кг(л)/га']) else ""
                    price_str = str(row['Цена за ед. (с НДС) в руб.']).strip() if pd.notna(row['Цена за ед. (с НДС) в руб.']) else ""
                    try:
                        price = float(price_str.replace(',', '.'))
                    except:
                        sheet_skipped += 1
                        self.skipped_items.append((sheet_name, name, "Некорректная цена."))
                        continue

                    # Определяем тип: если current_type установлен, используем его, иначе fallback на имя листа
                    if current_type:
                        ptype = current_type
                    else:
                        ptype = type_variants.get(sheet_name.strip().upper(), sheet_name.capitalize())

                    # Получаем type_id
                    if ptype not in type_map:
                        cursor.execute("INSERT INTO pesticide_types (type_name) VALUES (?)", (ptype,))
                        type_id = cursor.lastrowid
                        type_map[ptype] = type_id
                    else:
                        type_id = type_map[ptype]

                    if name not in existing:
                        # Новый препарат
                        cursor.execute('''
                            INSERT INTO pesticides (name, description, application_rate, packaging, price, manufacturer, pesticide_type_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (name, "", rate, packaging, price, manufacturer, type_id))
                        pesticide_id = cursor.lastrowid
                        substances = self._parse_substances(composition)
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
                            cursor.execute("SELECT 1 FROM pesticide_active_substances WHERE pesticide_id = ? AND substance_id = ?", (pesticide_id, substance_id))
                            if not cursor.fetchone():
                                cursor.execute('''
                                    INSERT INTO pesticide_active_substances (pesticide_id, substance_id, concentration)
                                    VALUES (?, ?, ?)
                                ''', (pesticide_id, substance_id, concentration))
                        sheet_new += 1
                        total_new += 1
                        existing[name] = {'id': pesticide_id}
                    else:
                        # Обновление существующего
                        old = existing[name]
                        update_fields = []
                        params = []
                        if price != old['price']:
                            update_fields.append("price = ?")
                            params.append(price)
                        if rate and rate != old['application_rate']:
                            update_fields.append("application_rate = ?")
                            params.append(rate)
                        if packaging and packaging != old['packaging']:
                            update_fields.append("packaging = ?")
                            params.append(packaging)
                        if manufacturer and manufacturer != old['manufacturer']:
                            update_fields.append("manufacturer = ?")
                            params.append(manufacturer)
                        if ptype and old.get('pesticide_type_id') != type_id:
                            update_fields.append("pesticide_type_id = ?")
                            params.append(type_id)
                        if update_fields:
                            sql = f"UPDATE pesticides SET {', '.join(update_fields)} WHERE id = ?"
                            params.append(old['id'])
                            cursor.execute(sql, params)
                            sheet_updated += 1
                        else:
                            sheet_unchanged += 1
                        if composition:
                            # Заменяем ДВ
                            cursor.execute("DELETE FROM pesticide_active_substances WHERE pesticide_id = ?", (old['id'],))
                            substances = self._parse_substances(composition)
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
                                cursor.execute('''
                                    INSERT INTO pesticide_active_substances (pesticide_id, substance_id, concentration)
                                    VALUES (?, ?, ?)
                                ''', (old['id'], substance_id, concentration))
                            if not update_fields:
                                sheet_updated += 1
                                sheet_unchanged -= 1

                processed_sheets += 1
                total_new += sheet_new
                total_updated += sheet_updated
                total_unchanged += sheet_unchanged
                total_skipped += sheet_skipped
                report_lines.append(f"Лист '{sheet_name}': новых {sheet_new}, обновлено {sheet_updated}, без изменений {sheet_unchanged}, пропущено {sheet_skipped}")

            self.current_import_stats = {
                'report': report_lines,
                'new': total_new,
                'updated': total_updated,
                'unchanged': total_unchanged,
                'skipped': total_skipped,
                'sheets': processed_sheets,
                'cursor': cursor
            }
            self.show_update_report_dialog()
        except Exception as e:
            if 'cursor' in locals():
                cursor.execute("ROLLBACK")
            self.show_message(f"Ошибка при парсинге: {e}")
            import traceback
            traceback.print_exc()

    def show_update_report_dialog(self):
        """Диалог отчёта для обновления (аналогичный импорту)"""
        stats = self.current_import_stats
        report_text = f"Обработано листов: {stats['sheets']}\n"
        report_text += f"Новых препаратов: {stats['new']}\n"
        report_text += f"Обновлено: {stats['updated']}\n"
        report_text += f"Без изменений: {stats['unchanged']}\n"
        report_text += f"Пропущено (неверная цена): {stats['skipped']}\n\n"
        if stats.get('report'):
            report_text += "\nДетали по листам:\n" + "\n".join(stats['report'])
        label = MDLabel(
            text=report_text,
            size_hint_y=None,
            halign='left',
            valign='top',
            padding=(10, 10)
        )
        label.bind(texture_size=label.setter('size'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(label)

        btn_cancel = MDFlatButton(
            text="Отмена",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.cancel_import()
        )
        btn_skipped = MDFlatButton(
            text="Подробнее",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.show_skipped_dialog()
        )
        btn_confirm = MDRaisedButton(
            text="Принять",  # или "Обновить"
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.confirm_import()
        )

        btn_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=10, padding=[10,5,10,5])
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_skipped)
        btn_box.add_widget(btn_confirm)
        content = MDBoxLayout(
            orientation='vertical', 
            spacing=10, 
            size_hint_y=None, 
            # height=scroll.height + btn_box.height + 20
            height=dp(150)
            )
        content.add_widget(scroll)
        content.add_widget(btn_box)
        dialog = MDDialog(title="Результат обновления",
                           type="custom", 
                           content_cls=content, 
                           size_hint=(0.9, 0.9), auto_dismiss=False)
        dialog.open()
        self.dialog = dialog

    def show_template_dialog(self, template_type):
        """Показывает диалог с описанием колонок и кнопками Закрыть/Сохранить"""
        if template_type == 'pesticides':
            info = (
                "Шаблон для импорта препаратов.\n\n"
                "Колонки:\n"
                "  • Препараты\n"
                "  • Состав\n"
                "  • Производитель\n"
                "  • Упаковка\n"
                "  • Норма расхода, кг(л)/га\n"
                "  • Цена за ед. (с НДС) в руб.\n\n"
                "Пример строки:\n"
                "  Препарат А, ДВ1 100 г/л; ДВ2 50 г/л, ООО ХимПром, 5 л, 0,5, 2500"
            )
        else:  # descriptions
            info = (
                "Шаблон для импорта описаний.\n\n"
                "Колонки:\n"
                "  • Название\n"
                "  • Культуры\n"
                "  • Болезни\n"
                "  • Описание\n\n"
                "Пример строки:\n"
                "  Препарат А, Пшеница, Ячмень, Мучнистая роса, Парша, "
                "Фунгицид широкого спектра действия"
            )

        content = MDBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        content.height = dp(250)

        label = MDLabel(text=info, size_hint_y=None, halign='left', valign='top')
        label.bind(texture_size=label.setter('size'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(label)
        content.add_widget(scroll)

        btn_box = MDBoxLayout(size_hint_y=None, height=48, spacing=10)

        btn_close = MDFlatButton(
            text="Закрыть",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.close_dialog()
            )
        btn_save = MDRaisedButton(
            text="Сохранить",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.save_template(template_type)
            )
        
        btn_box.add_widget(btn_close)
        btn_box.add_widget(btn_save)
        content.add_widget(btn_box)

        self.dialog = MDDialog(
            title="Экспорт шаблона",
            type="custom",
            content_cls=content,
            size_hint=(0.85, 0.6),
            auto_dismiss=False
        )
        self.dialog.open()


    def save_template(self, template_type):
        """Создаёт Excel-шаблон и сохраняет его в выбранное место"""
        # Закрываем диалог с описанием
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

        # Создаём DataFrame с нужными колонками
        if template_type == 'pesticides':
            df = pd.DataFrame(columns=[
                'Препараты', 'Состав', 'Производитель', 'Упаковка',
                'Норма расхода, кг(л)/га', 'Цена за ед. (с НДС) в руб.'
            ])
            # Примеры строк
            df.loc[0] = ['Препарат А', 'ДВ1 100 г/л; ДВ2 50 г/л', 'ООО ХимПром', '5 л', '0,5', '2500']
            df.loc[1] = ['Препарат Б', 'ДВ3 200 г/кг', 'ЗАО АгроХим', '1 кг', '0,2', '1800']
        else:  # descriptions
            df = pd.DataFrame(columns=['Название', 'Культуры', 'Болезни', 'Описание'])
            df.loc[0] = [
                'Препарат А',
                'Пшеница, Ячмень',
                'Мучнистая роса, Парша',
                'Фунгицид широкого спектра действия'
            ]
            df.loc[1] = [
                'Препарат Б',
                'Яблоня',
                'Парша, Плодовая гниль',
                'Системный фунгицид для защиты яблони'
            ]
        def on_file_saved(file_path):
            try:
                df.to_excel(file_path, index=False)
                self.show_message(f"Шаблон сохранён: {os.path.basename(file_path)}")
            except Exception as e:
                self.show_message(f"Ошибка сохранения: {e}")

        self._save_file_dialog(
            title="Сохранить шаблон",
            filters=[("Excel files", "*.xlsx")],
            default_name=f"template_{template_type}.xlsx",
            on_success=on_file_saved
        )


    def cancel_import(self):
        """Отмена: откатываем транзакцию"""
        self.close_skipped_dialog()   # закрываем пропуски, если открыты
        if hasattr(self, 'current_import_stats') and self.current_import_stats.get('cursor'):
            self.current_import_stats['cursor'].execute("ROLLBACK")
        self.close_dialog()
        self.show_message("Импорт отменён.")
        self.current_import_stats = None

    def _parse_substances(self, composition_str):
        if not composition_str:
            return []
        import re
        # Разделяем по + или ; с пробелами
        fragments = re.split(r'\s*[+;]\s*', composition_str)
        result = []
        conc_pattern = re.compile(r'([\d,\.]+\s*(?:г/кг|г/л|%|мг/кг|мг/л))')

        for frag in fragments:
            frag = frag.strip()
            if not frag:
                continue
            match = conc_pattern.search(frag)
            if match:
                conc = match.group(1).strip()
                # Убираем концентрацию из строки, остальное – название
                name = frag[:match.start()].strip() + " " + frag[match.end():].strip()
                name = name.strip()
                if not name and result:
                    # Если концентрация была в начале, а название не выделилось,
                    # используем название предыдущего вещества (редкий случай)
                    name = result[-1][0]
                result.append((name, conc))
            else:
                # Нет концентрации – дописываем к последнему названию
                if result:
                    last_name, last_conc = result[-1]
                    new_name = f"{last_name} {frag}".strip()
                    result[-1] = (new_name, last_conc)
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

    def show_export_dialog(self, data_type):
        """Показать диалог экспорта"""
        if data_type == "каталог":
            self.dialog = MDDialog(
                title="Экспорт каталога",
                text="Экспортировать полный каталог препаратов (включая культуры, болезни и описания)?",
                
                buttons=[
                    MDRaisedButton(
                        text="Отмена",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color="green",
                        on_release=lambda x: self.close_dialog()
                    ),
                    MDRaisedButton(
                        text="Экспорт",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color="green",
                        on_release=lambda x: self.export_full_catalog()
                    ),
                ],
                size_hint=(0.8, None),
                height="200dp"
            )
            self.dialog.open()
    
    def export_full_catalog(self):
        self.close_dialog()  # закрываем диалог подтверждения
        try:
            app = MDApp.get_running_app()
            db = app.db
            cursor = db.connection.cursor()

            # Получаем все препараты с типами
            cursor.execute('''
                SELECT p.id, p.name, p.description, p.application_rate, p.packaging,
                    p.price, p.manufacturer, pt.type_name
                FROM pesticides p
                LEFT JOIN pesticide_types pt ON p.pesticide_type_id = pt.id
                ORDER BY pt.type_name, p.name
            ''')
            pesticides = cursor.fetchall()

            if not pesticides:
                self.show_message("Нет данных для экспорта")
                return

            data_rows = []
            for pest in pesticides:
                pid = pest['id']
                # Действующие вещества
                cursor.execute('''
                    SELECT s.substance_name, pas.concentration
                    FROM pesticide_active_substances pas
                    JOIN active_substances s ON pas.substance_id = s.id
                    WHERE pas.pesticide_id = ?
                ''', (pid,))
                substances_list = [f"{row['substance_name']} {row['concentration']}" for row in cursor.fetchall()]
                substances_str = "; ".join(substances_list) if substances_list else ""

                # Культуры
                cursor.execute('''
                    SELECT c.culture_name
                    FROM pesticide_cultures pc
                    JOIN cultures c ON pc.culture_id = c.id
                    WHERE pc.pesticide_id = ?
                ''', (pid,))
                cultures_list = [row['culture_name'] for row in cursor.fetchall()]
                cultures_str = ", ".join(cultures_list) if cultures_list else ""

                # Болезни
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
                    'Тип': pest['type_name'],
                    'Действующие вещества': substances_str,
                    'Описание': pest['description'] or '',
                    'Норма расхода': pest['application_rate'] or '',
                    'Фасовка': pest['packaging'] or '',
                    'Цена, руб.': pest['price'],
                    'Производитель': pest['manufacturer'] or '',
                    'Культуры': cultures_str,
                    'Болезни': diseases_str,
                })

            df = pd.DataFrame(data_rows)

            def on_file_saved(file_path):
                try:
                    df.to_excel(file_path, index=False)
                    self.show_message(f"Каталог сохранён: {os.path.basename(file_path)}")
                except Exception as e:
                    self.show_message(f"Ошибка сохранения: {e}")

            self._save_file_dialog(
                title="Сохранить каталог",
                filters=[("Excel files", "*.xlsx")],
                default_name="catalog_full.xlsx",
                on_success=on_file_saved
            )
        except Exception as e:
            self.show_message(f"Ошибка экспорта: {e}")
    
    def export_data(self, data_type):
        """Заглушка для экспорта данных"""
        print(f" Экспорт {data_type} в Excel")
        self.show_message(f"Экспорт {data_type} выполнен успешно!")
        self.close_dialog()
    
    def update_database(self):
        """Заглушка для обновления БД"""
        print(" Обновление базы данных")
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

    def confirm_clear_except_models(self):
        self.dialog = MDDialog(
            title="Очистка данных",
            text="Эта операция удалит все препараты, клиентов, заказы. Продолжить?",
            buttons=[
                MDFlatButton(
                    text="Отмена",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color="green",
                    on_release=lambda x: self.close_dialog()),
                MDRaisedButton(
                    text="Очистить",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color="green",
                    on_release=lambda x: self.clear_database_except_models())
            ]
        )
        self.dialog.open()
    
    def show_info_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="white",
                    md_bg_color="green",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

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
    