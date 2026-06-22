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
from kivymd.app import MDApp

from app.ml.inference import PlantModel
import os 
from kivy.utils import platform


# На Android используем Plyer, на Windows – tkinter (старый код)
if platform == 'android':
    from plyer import camera, filechooser
else:
    camera = None
    filechooser = None
    # На десктопе остаётся tkinter для файлового диалога
    from tkinter import filedialog, Tk

import shutil

from app.ml.inference import species_ru, disease_ru   # в начало файла
import numpy as np

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
            md_bg_color:  [0.95, 0.95, 0.95, 1]    # светло-серый фон
            
            MDLabel:
                text: "Диагностика заболеваний"
                font_style: "H6"
                size_hint_x: 1
                size_hint_y: 1                  # занимает всю высоту
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)      
                halign: "center"
                valign: "middle"
            
            MDIconButton:
                icon: "help-circle-outline"
                theme_icon_color: "Custom"
                icon_color: "green"        # белая иконка
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
                on_release: root._on_clear_pressed()
        
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
                    
        # Кнопки анализа и сброса (фиксированная высота, изначально невидимы)
        MDBoxLayout:
            id: action_buttons
            orientation: "horizontal"
            size_hint_y: None
            height: dp(48)              # всегда занимает место
            spacing: dp(20)
            padding: [dp(10), 0, dp(10), 0]
            opacity: 0                  # невидимы
            disabled: True              # неактивны

            MDIconButton:
                id: analyze_btn
                icon: "magnify"
                theme_icon_color: "Custom"
                icon_color: "white"
                md_bg_color: "green"
                size_hint_x: 0.5
                on_release: root.start_analysis()

            MDIconButton:
                id: reset_btn
                icon: "close-circle"
                theme_icon_color: "Custom"
                icon_color: "white"
                md_bg_color: "green"
                size_hint_x: 0.5
                on_release: root.reset_image()
        
        # Кнопки выбора источника (всегда видны)
        MDBoxLayout:
            id: source_buttons
            orientation: "horizontal"
            size_hint_y: None
            height: dp(48)
            spacing: dp(20)
            padding: [dp(10), 0, dp(10), 0]
                    
            MDIconButton:
                id: gallery_btn
                icon: "image"
                theme_icon_color: "Custom"
                icon_color: "white"
                md_bg_color: "green"
                size_hint_x: 0.5
                on_release: root.use_gallery()
                    
            MDIconButton:
                id: camera_btn
                icon: "camera"
                theme_icon_color: "Custom"
                icon_color: "white"
                md_bg_color: "green"
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
        self.current_result = None
        self.mask_active = False
        # Загружаем модели сразу после запуска (отложенно, чтобы не тормозить UI)
        Clock.schedule_once(lambda dt: self.model.load_models(), 0.5)  
    
    def _add_action_buttons(self):
        """Показать кнопки действий (Анализировать, Сбросить)"""
        self.ids.action_buttons.opacity = 1
        self.ids.action_buttons.disabled = False
        
    def _remove_action_buttons(self):
        """Скрыть и отключить кнопки действий"""
        self.ids.action_buttons.opacity = 0
        self.ids.action_buttons.disabled = True



    def use_camera(self):
        if platform == 'android':
            try:
                self.camera_callback = self._on_camera_success
                camera.take_picture(filename=os.path.join(self._get_cache_dir(), 'camera_photo.jpg'),
                                    on_complete=self.camera_callback)
            except Exception as e:
                self.show_error("Камера", f"Ошибка камеры: {e}")
        else:
            print("📷 Камера (будет реализовано позже)")
            self.show_message("Камера", "Функция камеры в разработке")

    def use_gallery(self):
        if self.opening_dialog:
            return
        self.opening_dialog = True
        if platform == 'android':
            try:
                filechooser.open_file(title="Выберите изображение",
                                    filters=[["Изображения", "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"]],
                                    on_selection=self._on_gallery_selection)
            except Exception as e:
                self.show_error("Галерея", f"Ошибка галереи: {e}")
                self.opening_dialog = False
        else:
            self._open_file_dialog()   # старый tkinter-диалог

    def _on_gallery_selection(self, selection):
        self.opening_dialog = False
        if selection and len(selection) > 0:
            file_path = selection[0]
            Clock.schedule_once(lambda dt: self.load_image(file_path), 0)
        else:
            print("❌ Выбор отменён")

    def _on_camera_success(self, file_path):
        if file_path and os.path.exists(file_path):
            dest = os.path.join(self._get_cache_dir(), 'camera_photo.jpg')
   
            shutil.copy(file_path, dest)
            Clock.schedule_once(lambda dt: self.load_image(dest), 0)
        else:
            self.show_error("Камера", "Не удалось получить снимок")

    def _get_cache_dir(self):
        if platform == 'android':
            from android.storage import app_storage_path
            return app_storage_path()
        else:
            return os.path.join(os.getcwd(), 'temp')
   


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
            self.mask_active = False
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

    def _format_result_text(self, result):
        """Форматирует текст результата с процентами по правилам"""
        THRESHOLD = 0.9
        species_probs = result.get('species_probs')
        disease_probs = result.get('disease_probs')
        species_idx = result['species_idx']
        disease_idx = result['disease_idx']
        species_conf = result['species_conf']
        disease_conf = result['disease_conf']
        
        # Вид
        if species_conf >= THRESHOLD:
            species_text = species_ru.get(species_idx, result['species'])
        else:
            # топ-3
            indices = np.argsort(species_probs)[::-1][:3]
            items = []
            for i in indices:
                name = species_ru.get(i, 'Неизвестно')
                prob = species_probs[i] * 100
                items.append(f"{name} ({prob:.1f}%)")
            species_text = "не уверен, возможные варианты\n" + "\n".join(items)
        
        # Болезнь
        if disease_conf >= THRESHOLD:
            disease_text = disease_ru.get(disease_idx, result['disease'])
        else:
            indices = np.argsort(disease_probs)[::-1][:3]
            items = []
            for i in indices:
                name = disease_ru.get(i, 'Неизвестно')
                prob = disease_probs[i] * 100
                items.append(f"{name} ({prob:.1f}%)")
            disease_text = "не уверен, возможные варианты\n" + "\n".join(items)
        species_part = f"[color=006400]Вид:[/color] {species_text}"
        disease_part = f"[color=006400]Болезнь:[/color] {disease_text}"
        # return f"Вид: {species_text}\n\nБолезнь: {disease_text}"
        return f"{species_part}\n\n{disease_part}"

    def show_analysis_result(self, result):
        """Показать результат анализа в нижней части экрана"""
        self.current_result = result
        self.mask_active = True
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
            text_color=(0, 0.25, 0, 1),   # зелёный цвет
            size_hint_y=None,
            height=dp(30),
            halign="center"
        )
        # Вместо обычного MDLabel используем ScrollView + MDLabel для длинного текста
        from kivy.uix.scrollview import ScrollView
        text_content = MDLabel(
            # text=f"Вид: {result['species']}\n\nБолезнь: {result['disease']}",
            text=self._format_result_text(result),
            markup=True,              # разрешить теги
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
        # Кнопка "Подобрать препарат"
        btn_find = MDRaisedButton(
            text="Подобрать препарат",
            size_hint_x=0.4,
            icon="magnify",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            on_release=lambda x: self.find_pesticides()
        )
        button_box.add_widget(Widget())  # пустой виджет слева для отступа

        close_btn = MDRaisedButton(
            text="Закрыть",
            icon="close",
            theme_text_color="Custom",
            text_color="white",
            md_bg_color="green",
            size_hint_x=0.3,
            on_release=lambda x: self.remove_result_widget(result_layout)
        )
        button_box.add_widget(btn_find)
        button_box.add_widget(close_btn)

        result_layout.add_widget(title)
        result_layout.add_widget(scroll)
        result_layout.add_widget(button_box)

        self.add_widget(result_layout)
        self.current_result_widget = result_layout

    def find_pesticides(self):
        if not self.current_result:
            return
        res = self.current_result
        THRESHOLD = 0.9
        species_probs = np.array(res['species_probs'])
        disease_probs = np.array(res['disease_probs'])

        if res['species_conf'] >= THRESHOLD:
            species_indices = [res['species_idx']]
        else:
            species_indices = list(np.argsort(species_probs)[::-1][:3])
        if res['disease_conf'] >= THRESHOLD:
            disease_indices = [res['disease_idx']]
        else:
            disease_indices = list(np.argsort(disease_probs)[::-1][:3])

        species_names = [species_ru.get(i, '') for i in species_indices]
        disease_names = [disease_ru.get(i, '') for i in disease_indices]
        species_names = [n for n in species_names if n and 'неизвест' not in n.lower()]
        disease_names = [n for n in disease_names if n and 'неизвест' not in n.lower()]

        print("DEBUG: species_names =", species_names)
        print("DEBUG: disease_names =", disease_names)

        # Передаём фильтры через главный экран до переключения вкладки
        app = MDApp.get_running_app()
        main_screen = app.screen_manager.get_screen('main')
        main_screen.switch_to_catalog_with_filters(species_names, disease_names)


    def remove_result_widget(self, widget):
        """Удалить виджет результата"""
        if widget.parent:
            widget.parent.remove_widget(widget)
        # # Возвращаем исходное изображение
        # if hasattr(self, 'original_image_path') and self.original_image_path:
        #     self.ids.selected_image.source = self.original_image_path
        #     self.ids.selected_image.reload()
        self.enable_buttons()
           
    def _on_clear_pressed(self):
        if self.mask_active:
            # Сбросить только маску, вернуть оригинал
            if hasattr(self, 'original_image_path') and self.original_image_path:
                self.ids.selected_image.source = self.original_image_path
                self.ids.selected_image.reload()
                self.mask_active = False
                self.ids.clear_btn.icon = "close-circle"
                print(" Маска снята")
        else:
            # Полный сброс изображения
            self.reset_image()

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
        """Показать полный справочник диагнозов"""
        help_text = (
            "1. Нажмите «Галерея» и выберите фото растения.\n"
            "2. Нажмите «Анализировать».\n"
            "3. Получите результат.\n\n"
            " Диагностируемые виды и болезни:\n\n"
            "Яблоня:\n"
            "  • Альтернариоз яблони\n"
            "  • Бурая пятнистость яблони\n"
            "  • Парша\n"
            "  • Парша яблони\n"
            "  • Ржавчина можжевельника-яблони\n"
            "  • Серая пятнистость яблони\n"
            "  • Чёрная гниль\n\n"
            "Сладкий перец:\n"
            "  • Бактериальная пятнистость перца\n\n"
            "Вишня:\n"
            "  • Мучнистая роса\n\n"
            "Кукуруза:\n"
            "  • Обычная ржавчина кукурузы\n"
            "  • Северная листовая пятнистость кукурузы\n"
            "  • Серая листовая пятнистость кукурузы\n\n"
            "Виноград:\n"
            "  • Листовая пятнистость\n"
            "  • Чёрная гниль\n"
            "  • Эска\n\n"
            "Персик:\n"
            "  • Бактериальная пятнистость персика\n\n"
            "Картофель:\n"
            "  • Фитофтороз поздний\n"
            "  • Фитофтороз ранний\n\n"
            "Тыква:\n"
            "  • Мучнистая роса\n\n"
            "Клубника:\n"
            "  • Листовой ожог\n\n"
            "Томат:\n"
            "  • Бактериальная пятнистость томата\n"
            "  • Вирус желтой курчавости листьев томата\n"
            "  • Вирус мозаики томата\n"
            "  • Листовая плесень томата\n"
            "  • Паутинный клещ\n"
            "  • Септориоз томата\n"
            "  • Фитофтороз поздний\n"
            "  • Фитофтороз ранний\n"
            "  • Целевая пятнистость\n\n"
            "В случае если модель не может опознать растение, в ответе вы можете увидеть:\n"
            "  • Неизвестный объект, Болезнь - Неизвестно\n"
            "  • Неизвестное растение\n"
        )

        # Контейнер содержимого
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

        # Создаём диалог
        dialog = MDDialog(
            title="Справочная информация",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="Закрыть",
                    theme_text_color="Custom",
                    text_color=(0, 0.25, 0, 1),  # зелёный
                    on_release=lambda x: dialog.dismiss()
                )
            ],
            size_hint=(0.95, 0.85)
        )

        # Принудительно меняем цвет заголовка (обходим ограничения)
        # Ищем дочерний виджет с текстом заголовка
        def set_title_color(dialog_inst, dt):
            for child in dialog_inst.children:
                if hasattr(child, 'title') and hasattr(child, 'text_color'):
                    child.theme_text_color = "Custom"
                    # child.text_color = (0, 0.7, 0, 1)
                    child.text_color = 'green'
                    break
        Clock.schedule_once(lambda dt: set_title_color(dialog, dt), 0.1)

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