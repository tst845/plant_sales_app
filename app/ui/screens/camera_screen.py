from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp  # добавлен импорт dp
from kivy.core.image import Image as CoreImage

from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.progressbar import MDProgressBar

from tkinter import filedialog, Tk
import os
import random

Builder.load_string('''
#:import dp kivy.metrics.dp

<CameraScreen>:
    name: 'camera_screen'
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(10)
        
        MDTopAppBar:
            title: "Диагностика заболеваний"
            elevation: 4
            right_action_items: [["help-circle-outline", lambda x: root.show_help()]]
        
        # Область для изображения с крестиком (изначально крестик скрыт)
        RelativeLayout:
            size_hint_y: 1
            MDCard:
                id: image_card
                orientation: "vertical"
                size_hint: 1, 1
                padding: dp(10)
                elevation: 4
                md_bg_color: (0.95, 0.95, 0.95, 1)
                
                MDBoxLayout:
                    orientation: "vertical"
                    size_hint: 1, 1
                    
                    Image:
                        id: selected_image
                        allow_stretch: True
                        keep_ratio: True
                        source: ""
                        size_hint: 1, 1
            
            MDIconButton:
                id: clear_btn
                icon: "close-circle"
                theme_icon_color: "Custom"
                icon_color: "red"
                size_hint: None, None
                size: dp(48), dp(48)
                pos_hint: {"top": 1, "right": 1}
                opacity: 0
                disabled: True
                on_release: root.reset_image()
        
        # Статус и прогресс (изначально скрыты)
        MDBoxLayout:
            id: status_box
            orientation: "vertical"
            size_hint_y: None
            height: 0
            opacity: 0
            spacing: dp(5)
            
            MDProgressBar:
                id: progress_bar
                value: 0
                size_hint_y: None
                height: dp(8)
            
            MDLabel:
                id: status_label
                text: ""
                halign: "center"
                font_style: "Caption"
                size_hint_y: None
                height: dp(20)
                    
        # Кнопки действий (изначально пустой контейнер)
        MDBoxLayout:
            id: action_buttons
            orientation: "horizontal"
            size_hint_y: None
            height: 0
            spacing: dp(10)
            padding: dp(10)
        
        # Кнопки выбора источника (всегда видны)
        MDBoxLayout:
            id: source_buttons
            orientation: "horizontal"
            size_hint_y: None
            height: dp(100)
            spacing: dp(20)
            padding: dp(10)
                    
            MDRaisedButton:
                id: gallery_btn
                text: "Галерея"
                size_hint_x: 0.5
                on_release: root.use_gallery()
                    
            MDRaisedButton:
                id: camera_btn
                text: "Камера"
                size_hint_x: 0.5
                on_release: root.use_camera()
            
  
''')

class CameraScreen(Screen):
    """Упрощённый экран диагностики — без смены состояний"""
    
    selected_image_path = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress_interval = None
        self.opening_dialog = False          # блокировка повторного открытия диалога
        self.reset_in_progress = False       # блокировка повторного сброса
    
    def _add_action_buttons(self):
        """Добавить кнопки действий в контейнер"""
        action_buttons = self.ids.action_buttons
        action_buttons.clear_widgets()
        
        btn_analyze = MDRaisedButton(
            text="Анализировать",
            icon="brain",
            size_hint_x=0.5,
            on_release=lambda x: self.start_analysis()
        )
        btn_reset = MDRaisedButton(
            text="Сбросить",
            icon="close-circle",
            size_hint_x=0.5,
            md_bg_color="gray",
            on_release=lambda x: self.reset_image()
        )
        action_buttons.add_widget(btn_analyze)
        action_buttons.add_widget(btn_reset)
        action_buttons.height = dp(60)
        action_buttons.opacity = 1

    def _remove_action_buttons(self):
        """Удалить кнопки действий"""
        self.ids.action_buttons.clear_widgets()
        self.ids.action_buttons.height = 0
        self.ids.action_buttons.opacity = 0

    def use_camera(self):
        """Заглушка для камеры"""
        print("📷 Камера (будет реализовано позже)")
        self.show_message("Камера", "Функция камеры в разработке")
    
    def use_gallery(self):
        """Выбор файла из галереи"""
        if self.opening_dialog:
            print("⚠️ Диалог уже открыт, игнорирую повторный вызов")
            return
        print("🖼️ Открываем галерею")
        self.opening_dialog = True
        self._open_file_dialog()

    def _open_file_dialog(self):
        Clock.schedule_once(lambda dt: self._real_open_file_dialog(), 0.1)

    def _real_open_file_dialog(self):
        try:
            root = Tk()
            root.withdraw()
            default_dir = r"G:\Datasets_origins\balanced_plant_dataset\images"
            if not os.path.exists(default_dir):
                default_dir = os.getcwd()
            file_path = filedialog.askopenfilename(
                initialdir=default_dir,
                title="Выберите изображение растения",
                filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff")]
            )
            root.destroy()
            if file_path:
                print(f"✅ Выбран файл: {file_path}")
                self.load_image(file_path)
            else:
                print("❌ Выбор отменён")
        except Exception as e:
            print(f"Ошибка диалога: {e}")
            self.show_message("Ошибка", f"Не удалось открыть диалог: {e}")
        finally:
            self.opening_dialog = False

    def load_image(self, file_path):
        """Загрузить изображение в виджет"""
        if self.selected_image_path == file_path:
            return
        self.selected_image_path = file_path
        image_widget = self.ids.selected_image
        image_widget.source = file_path
        image_widget.reload()
        # Добавляем кнопки действий
        self._add_action_buttons()
        # Показываем крестик
        self.ids.clear_btn.opacity = 1
        self.ids.clear_btn.disabled = False
        print(f"📸 Изображение загружено, размер виджета: {image_widget.size}")

    def reset_image(self):
        """Очистить изображение и вернуться к исходному виду"""
        if self.reset_in_progress:
            return
        self.reset_in_progress = True
        try:
            if not self.selected_image_path and self.ids.selected_image.source == "":
                return
            self.ids.selected_image.source = ""
            self.ids.selected_image.reload()
            self.selected_image_path = ""
            # Удаляем кнопки действий
            self._remove_action_buttons()
            # Скрываем крестик
            self.ids.clear_btn.opacity = 0
            self.ids.clear_btn.disabled = True
            # Скрываем прогресс
            self.ids.progress_bar.value = 0
            self.ids.status_box.height = 0
            self.ids.status_box.opacity = 0
            if self.progress_interval:
                Clock.unschedule(self.progress_interval)
                self.progress_interval = None
            print("🔄 Изображение сброшено")
        finally:
            self.reset_in_progress = False
    
    def start_analysis(self):
        """Запуск симуляции анализа"""
        if self.progress_interval is not None:
            print("⚠️ Анализ уже запущен")
            return
        if not self.selected_image_path:
            self.show_message("Ошибка", "Сначала выберите изображение")
            return
        print("🧠 Начинаем анализ")
        # Показать прогресс
        self.ids.status_box.height = dp(30)
        self.ids.status_box.opacity = 1
        self.ids.progress_bar.value = 0
        self.ids.status_label.text = "Обработка..."
        self.progress_interval = Clock.schedule_interval(self.update_progress, 0.5)
    
    def update_progress(self, dt):
        progress = self.ids.progress_bar.value + 25
        if progress >= 100:
            self.ids.progress_bar.value = 100
            self.ids.status_label.text = "Готово!"
            if self.progress_interval:
                Clock.unschedule(self.progress_interval)
                self.progress_interval = None
            Clock.schedule_once(lambda dt: self.finish_analysis(), 0.5)
        else:
            self.ids.progress_bar.value = progress
            self.ids.status_label.text = f"Обработка... {int(progress)}%"
            
    def finish_analysis(self):
        """Завершение анализа — показываем случайный результат, НЕ сбрасываем изображение"""
        if self.progress_interval:
            Clock.unschedule(self.progress_interval)
            self.progress_interval = None
        result_type = random.choice(["success", "unknown", "error"])
        if result_type == "success":
            self.show_results()
        elif result_type == "unknown":
            self.show_unknown_result()
        else:
            self.show_error("Модель не загружена", "Не удалось загрузить модель нейросети")
        # Изображение остаётся на экране   
           
    def show_results(self):
        """Показать результаты (заглушка)"""
        dialog = MDDialog(
            title="Результат анализа",
            text="Заболевание: Мучнистая роса\nВероятность: 87%\n\nРекомендации:\n• Обработать фунгицидом 'Скор'\n• Удалить поражённые листья",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
        # self.reset_image()
    
    def show_unknown_result(self):
        dialog = MDDialog(
            title="Не удалось определить",
            text="Попробуйте сделать более чёткий снимок.",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
        # self.reset_image()
    
    def show_error(self, title, message):
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
        # self.reset_image()
    
    def show_help(self):
        dialog = MDDialog(
            title="Справка",
            text="1. Нажмите «Галерея» и выберите фото растения.\n2. Нажмите «Анализировать».\n3. Получите результат.",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def show_message(self, title, message):
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()