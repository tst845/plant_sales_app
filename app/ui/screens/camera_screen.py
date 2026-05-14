from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.widget import Widget   # добавьте эту строку
from kivy.uix.scrollview import ScrollView

from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.progressbar import MDProgressBar

from app.ml.inference import PlantModel
import os 

from tkinter import filedialog, Tk

Builder.load_string('''
#:import dp kivy.metrics.dp

<CameraScreen>:
    name: 'camera_screen'
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(10)
        
        # Кастомная шапка
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)                      # чуть больше для удобства
            padding: [dp(10), 0, dp(10), 0]
            spacing: dp(10)
            md_bg_color: app.theme_cls.primary_color    # тёмно-зелёный (можно поменять)
            
            MDLabel:
                text: "Диагностика заболеваний"
                font_style: "H6"
                size_hint_x: 1
                size_hint_y: 1                  # занимает всю высоту
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)       # белый текст на зелёном
                halign: "center"
                valign: "middle"
            
            MDIconButton:
                icon: "help-circle-outline"
                theme_icon_color: "Custom"
                icon_color: (0, 0, 0, 1)       # белая иконка
                size_hint: None, None
                size: dp(32), dp(32)           # увеличил размер для лучшего касания
                pos_hint: {"center_y": 0.5}    # центрирование внутри контейнера
                on_release: root.show_help()
        
        # Область для изображения с крестиком (изначально крестик скрыт)
        RelativeLayout:
            size_hint_y: 1
            MDCard:
                id: image_card
                orientation: "vertical"
                size_hint: 1, 1
                padding: dp(10)
                elevation: 1
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
        self.reset_in_progress = False # блокировка повторного сброса
        self.model = PlantModel()    
        # Загружаем модели сразу после запуска (отложенно, чтобы не тормозить UI)
        Clock.schedule_once(lambda dt: self.model.load_models(), 0.5)  
    
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
        self.original_image_path = file_path   # запомнили
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
        # Если есть временный файл маски, удалить
        if hasattr(self, 'current_masked_path') and self.current_masked_path:
            try:
                os.remove(self.current_masked_path)
            except:
                pass
            self.current_masked_path = None
    
    def start_analysis(self):
        """Запуск анализа через модель"""
        if not self.selected_image_path:
            self.show_message("Ошибка", "Сначала выберите изображение")
            return
        if not self.model.loaded:
            # Попытаемся загрузить модели (можно сделать при старте приложения)
            Clock.schedule_once(lambda dt: self.load_models_and_analyze(), 0)
        else:
            self._run_inference()
    
    def load_models_and_analyze(self):
        if not self.model.load_models():
            self.show_error("Ошибка модели", "Не удалось загрузить ONNX модели")
            return
        self._run_inference()

    def _run_inference(self):
        """Запуск инференса в отдельном потоке"""
        from threading import Thread
        self.ids.status_box.height = dp(30)
        self.ids.status_box.opacity = 1
        self.ids.progress_bar.value = 0
        self.ids.status_label.text = "Загрузка моделей..."

        def update_progress(value):
            Clock.schedule_once(lambda dt: self._update_progress_ui(value))

        def inference_thread():
            try:
                result = self.model.predict(self.selected_image_path, progress_callback=update_progress)
                Clock.schedule_once(lambda dt: self.show_analysis_result(result))
            except Exception as ex:
                print(f"Ошибка инференса: {ex}")
                Clock.schedule_once(lambda dt: self.show_error("Ошибка", str(ex)))

        self.thread = Thread(target=inference_thread, daemon=True)
        self.thread.start()

    def _update_progress_ui(self, value):
        self.ids.progress_bar.value = value * 100
        if value < 0.2:
            self.ids.status_label.text = "Сегментация листа..."
        elif value < 0.5:
            self.ids.status_label.text = "Анализ поражений..."
        elif value < 0.9:
            self.ids.status_label.text = "Классификация..."
        else:
            self.ids.status_label.text = "Готово!"

    def show_analysis_result(self, result):
        """Показать результат анализа в нижней части экрана"""
        self.disable_buttons()  # блокируем кнопки
        # Подменяем картинку на размеченную
        if 'masked_image_path' in result and result['masked_image_path']:
            self.current_masked_path = result['masked_image_path']
            self.ids.selected_image.source = result['masked_image_path']
            self.ids.selected_image.reload()
        # Скрываем прогресс-бар, если он был виден
        self.ids.status_box.height = 0
        self.ids.status_box.opacity = 0

        # Создаём контейнер результата
        result_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(210),           # уменьшенная высота (примерно 1/5 от 640)
            padding=dp(16),
            spacing=dp(8),
            md_bg_color=(1, 1, 1, 1),  # белый полупрозрачный фон
            pos_hint={'bottom': 1},
        )

        # Заголовок
        title = MDLabel(
            text="Результат диагностики",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),   # чёрный цвет
            size_hint_y=None,
            height=dp(30),
            halign="center"
        )
        # Вместо обычного MDLabel используем ScrollView + MDLabel для длинного текста
        from kivy.uix.scrollview import ScrollView
        text_content = MDLabel(
            text=f"Вид: {result['species']}\n\nБолезнь: {result['disease']}",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            size_hint_y=None,
            halign="left",
            valign="top"
        )
        text_content.bind(texture_size=text_content.setter('size'))
        scroll = ScrollView(size_hint_y=1, do_scroll_x=False)
        scroll.add_widget(text_content)

        # вместо прямого добавления text_content

        # Кнопка закрытия
        # Вместо прямого добавления close_btn:
        button_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        button_box.add_widget(Widget())  # пустой виджет слева для отступа
        close_btn = MDRaisedButton(
            text="Закрыть",
            size_hint_x=0.3,
            on_release=lambda x: self.remove_result_widget(result_layout)
        )
        button_box.add_widget(close_btn)

        result_layout.add_widget(title)
        result_layout.add_widget(scroll)
        result_layout.add_widget(button_box)

        self.add_widget(result_layout)
        self.current_result_widget = result_layout

    def remove_result_widget(self, widget):
        """Удалить виджет результата"""
        if widget.parent:
            widget.parent.remove_widget(widget)
        # Возвращаем исходное изображение
        if hasattr(self, 'original_image_path') and self.original_image_path:
            self.ids.selected_image.source = self.original_image_path
            self.ids.selected_image.reload()
        self.enable_buttons()
           
    def show_results(self):
        """Показать результаты (заглушка)"""
        dialog = MDDialog(
            title="Результат анализа",
            text="Заболевание: Мучнистая роса\nВероятность: 87%\n\nРекомендации:\n• Обработать фунгицидом 'Скор'\n• Удалить поражённые листья",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
        # self.reset_image()
    
    def disable_buttons(self):
        """Отключить все управляющие кнопки"""
        self.ids.camera_btn.disabled = True
        self.ids.gallery_btn.disabled = True
        self.ids.clear_btn.disabled = True
        # Отключаем кнопки в контейнере action_buttons (Анализировать, Сбросить)
        for child in self.ids.action_buttons.children:
            if hasattr(child, 'disabled'):
                child.disabled = True

    def enable_buttons(self):
        """Включить все управляющие кнопки"""
        self.ids.camera_btn.disabled = False
        self.ids.gallery_btn.disabled = False
        self.ids.clear_btn.disabled = False
        for child in self.ids.action_buttons.children:
            if hasattr(child, 'disabled'):
                child.disabled = False

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

    def cleanup_temp_files(self):
        if hasattr(self, 'current_masked_path') and self.current_masked_path:
            try:
                os.remove(self.current_masked_path)
            except:
                pass