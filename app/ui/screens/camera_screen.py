# app/ui/screens/camera_screen.py

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock

from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import ScrollView

import os
from datetime import datetime

Builder.load_string('''
#:import dp kivy.metrics.dp

<CameraScreen>:
    name: 'camera_screen'
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(10)
        
        # Шапка
        MDTopAppBar:
            title: "Диагностика заболеваний"
            elevation: 4
            right_action_items: [["help-circle-outline", lambda x: root.show_help()]]
           
        MDLabel:
            text: "Выберите источник изображения для анализа"
            halign: "center"
            font_style: "H6"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: dp(40)
        
        # Основная область - зависит от состояния
        BoxLayout:
            id: main_area
            orientation: "vertical"
            size_hint_y: 1
        
        # Кнопки действий (меняются в зависимости от состояния)
        MDBoxLayout:
            id: action_buttons
            size_hint_y: None
            height: dp(60)
            padding: dp(10)
            spacing: dp(10)

<SourceSelectionState>:
    orientation: "vertical"
    spacing: dp(20)
    padding: dp(20)
    
    MDLabel:
        # text: "Выберите способ получения изображения"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: dp(40)
    
    MDGridLayout:
        cols: 2
        spacing: dp(20)
        padding: dp(20)
        size_hint_y: None
        height: dp(300)
        
        MDCard:
            orientation: "vertical"
            size_hint: None, None
            size: dp(150), dp(150)
            padding: dp(15)
            spacing: dp(10)
            elevation: 4
            ripple_behavior: True
            on_release: root.use_camera()
            
            MDIconButton:
                icon: "camera"
                theme_icon_color: "Custom"
                icon_color: "green"
                size_hint: None, None
                size: dp(80), dp(80)
                pos_hint: {"center_x": 0.5}
            
            MDLabel:
                text: "Камера"
                halign: "center"
                font_style: "H6"
                size_hint_y: None
                height: dp(30)
        
        MDCard:
            orientation: "vertical"
            size_hint: None, None
            size: dp(150), dp(150)
            padding: dp(15)
            spacing: dp(10)
            elevation: 4
            ripple_behavior: True
            on_release: root.use_gallery()
            
            MDIconButton:
                icon: "image-multiple"
                theme_icon_color: "Custom"
                icon_color: "blue"
                size_hint: None, None
                size: dp(80), dp(80)
                pos_hint: {"center_x": 0.5}
            
            MDLabel:
                text: "Галерея"
                halign: "center"
                font_style: "H6"
                size_hint_y: None
                height: dp(30)

<CameraCaptureState>:
    orientation: "vertical"
    spacing: dp(15)
    padding: dp(10)
    
    MDLabel:
        text: "Снимок с камеры"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: dp(40)
    
    MDCard:
        id: preview_card
        orientation: "vertical"
        size_hint: None, None
        size: dp(300), dp(300)
        pos_hint: {"center_x": 0.5}
        padding: dp(10)
        elevation: 8
        
        MDBoxLayout:
            orientation: "vertical"
            
            # Заглушка для камеры
            MDLabel:
                text: "Камера (заглушка)"
                halign: "center"
                valign: "middle"
                size_hint: 1, 1
                font_style: "H4"
                theme_text_color: "Secondary"
    
    MDLabel:
        id: status_label
        text: "Готово к съемке"
        halign: "center"
        font_style: "Body1"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: dp(30)
    
    MDBoxLayout:
        size_hint_y: None
        height: dp(60)
        spacing: dp(20)
        padding: dp(10)
        
        MDRaisedButton:
            id: take_photo_btn
            text: "Сделать снимок"
            icon: "camera"
            size_hint_x: 0.5
            on_release: root.capture_action()
        
        MDRaisedButton:
            id: capture_action_button
            text: "Отмена"
            icon: "close"
            size_hint_x: 0.5
            md_bg_color: "gray"
            on_release: root.cancel_action()

<GallerySelectionState>:
    orientation: "vertical"
    spacing: dp(15)
    padding: dp(10)
    
    MDLabel:
        text: "Выбор из галереи"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: dp(40)
    
    ScrollView:
        MDGridLayout:
            cols: 3
            spacing: dp(10)
            padding: dp(10)
            adaptive_height: True
            
            # Тестовые изображения
            MDCard:
                size_hint: None, None
                size: dp(100), dp(100)
                padding: dp(5)
                on_release: root.select_test_image(1)
                
                MDLabel:
                    text: "Тест 1"
                    halign: "center"
                    valign: "middle"
                    size_hint: 1, 1
            
            MDCard:
                size_hint: None, None
                size: dp(100), dp(100)
                padding: dp(5)
                on_release: root.select_test_image(2)
                
                MDLabel:
                    text: "Тест 2"
                    halign: "center"
                    valign: "middle"
                    size_hint: 1, 1
            
            MDCard:
                size_hint: None, None
                size: dp(100), dp(100)
                padding: dp(5)
                on_release: root.select_test_image(3)
                
                MDLabel:
                    text: "Тест 3"
                    halign: "center"
                    valign: "middle"
                    size_hint: 1, 1
    
    MDLabel:
        text: "Выберите тестовое изображение или отмените выбор"
        halign: "center"
        font_style: "Body1"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: dp(40)

<ProcessingState>:
    orientation: "vertical"
    spacing: dp(20)
    padding: dp(40)
    
    MDLabel:
        text: "Обработка изображения"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: dp(40)
    
    MDProgressBar:
        id: progress_bar
        value: 0
        size_hint_y: None
        height: dp(10)
    
    MDLabel:
        id: processing_label
        text: "Подготовка изображения..."
        halign: "center"
        font_style: "Body1"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: dp(30)
    
    MDLabel:
        id: step_label
        text: "Шаг 1 из 4"
        halign: "center"
        font_style: "Caption"
        theme_text_color: "Hint"
        size_hint_y: None
        height: dp(20)

<AnalysisState>:
    orientation: "vertical"
    spacing: dp(20)
    padding: dp(40)
    
    MDLabel:
        text: "Анализ нейросетью"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: dp(40)
    
    MDProgressBar:
        type: "indeterminate"
        running: True
        size_hint_y: None
        height: dp(10)
    
    MDLabel:
        text: "Идет распознавание заболевания..."
        halign: "center"
        font_style: "Body1"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: dp(30)
    
    MDLabel:
        text: "Пожалуйста, подождите"
        halign: "center"
        font_style: "Caption"
        theme_text_color: "Hint"
        size_hint_y: None
        height: dp(20)

<ErrorState>:
    orientation: "vertical"
    spacing: dp(20)
    padding: dp(40)
    
    MDIconButton:
        icon: "alert-circle-outline"
        theme_icon_color: "Custom"
        icon_color: "red"
        size_hint: None, None
        size: dp(80), dp(80)
        pos_hint: {"center_x": 0.5}
    
    MDLabel:
        id: error_title
        text: "Произошла ошибка"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: dp(40)
    
    MDLabel:
        id: error_message
        text: "Что-то пошло не так"
        halign: "center"
        font_style: "Body1"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: dp(60)
    
    MDBoxLayout:
        size_hint_y: None
        height: dp(50)
        spacing: dp(20)
        padding: dp(10)
        
        MDFlatButton:
            text: "Повторить"
            on_release: root.parent.parent.retry_analysis()
        
        MDRaisedButton:
            text: "В начало"
            on_release: root.parent.parent.back_to_start()

<ResultState>:
    orientation: "vertical"
    spacing: dp(15)
    padding: dp(20)
    
    MDLabel:
        text: "Результаты анализа"
        halign: "center"
        font_style: "H4"
        size_hint_y: None
        height: dp(50)
    
    MDCard:
        orientation: "vertical"
        padding: dp(15)
        spacing: dp(10)
        elevation: 4
        
        MDLabel:
            id: result_title
            text: "Заболевание обнаружено"
            halign: "center"
            font_style: "H5"
            size_hint_y: None
            height: dp(40)
        
        MDLabel:
            id: result_name
            text: "Мучнистая роса"
            halign: "center"
            font_style: "H6"
            theme_text_color: "Primary"
            size_hint_y: None
            height: dp(30)
        
        MDLabel:
            id: result_confidence
            text: "Вероятность: 85%"
            halign: "center"
            font_style: "Body1"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: dp(25)
    
    ScrollView:
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(10)
            size_hint_y: None
            height: self.minimum_height
            
            MDLabel:
                text: "Рекомендации:"
                font_style: "H6"
                size_hint_y: None
                height: dp(30)
            
            MDLabel:
                id: recommendations
                text: "• Обработать фунгицидом 'Скор'\\n• Удалить пораженные листья\\n• Обеспечить хорошую вентиляцию"
                size_hint_y: None
                height: self.texture_size[1] + dp(20)
            
            MDLabel:
                text: "Препараты:"
                font_style: "H6"
                size_hint_y: None
                height: dp(30)
            
            MDLabel:
                id: pesticides
                text: "• Скор (0.2 л/га)\\n• Топаз (0.1 л/га)\\n• Фундазол (0.5 кг/га)"
                size_hint_y: None
                height: self.texture_size[1] + dp(20)
    
    MDBoxLayout:
        size_hint_y: None
        height: dp(60)
        spacing: dp(10)
        padding: dp(10)
        
        MDRaisedButton:
            text: "Открыть каталог"
            icon: "view-list"
            size_hint_x: 0.5
            on_release: root.parent.parent.open_catalog()
        
        MDRaisedButton:
            text: "Сбросить"
            icon: "refresh"
            size_hint_x: 0.5
            on_release: root.parent.parent.reset_analysis()

<UnknownResultState>:
    orientation: "vertical"
    spacing: dp(20)
    padding: dp(40)
    
    MDIconButton:
        icon: "help-circle"
        theme_icon_color: "Custom"
        icon_color: "orange"
        size_hint: None, None
        size: dp(80), dp(80)
        pos_hint: {"center_x": 0.5}
    
    MDLabel:
        text: "Не удалось определить заболевание"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: dp(40)
    
    MDLabel:
        text: "Попробуйте сделать более четкий снимок или выбрать другое изображение"
        halign: "center"
        font_style: "Body1"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: dp(60)
    
    MDBoxLayout:
        size_hint_y: None
        height: dp(50)
        spacing: dp(20)
        padding: dp(10)
        
        MDFlatButton:
            text: "Повторить"
            on_release: root.parent.parent.retry_analysis()
        
        MDRaisedButton:
            text: "В начало"
            on_release: root.parent.parent.back_to_start()
''')

# Состояния интерфейса
class SourceSelectionState(MDBoxLayout):
    """Состояние выбора источника изображения"""
    def use_camera(self):
        """Прокси метод для вызова CameraScreen"""
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'screen_manager'):
            for screen in app.screen_manager.screens:
                if screen.name == 'camera_screen':
                    screen.use_camera()
                    break
    
    def use_gallery(self):
        """Прокси метод для вызова CameraScreen"""
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'screen_manager'):
            for screen in app.screen_manager.screens:
                if screen.name == 'camera_screen':
                    screen.use_gallery()
                    break

class CameraCaptureState(MDBoxLayout):
    """Состояние съемки с камеры"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def capture_action(self):
        """Обработка нажатия кнопки 'Сделать снимок'"""
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'screen_manager'):
            for screen in app.screen_manager.screens:
                if screen.name == 'camera_screen':
                    screen.capture_photo()
                    self.update_button_state(True)
                    break


    def update_buttons(self, photo_captured):
        """Обновить состояние кнопки"""
        button = self.ids.capture_action_button
        if photo_captured:
            button.text = "Готово"
            button.icon = "check"
            button.md_bg_color = "green"
        else:
            button.text = "Отмена"
            button.icon = "close"
            button.md_bg_color = "gray"
    
    def cancel_action(self):
        """Обработка нажатия кнопки 'Отмена/Готово'"""
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'screen_manager'):
            for screen in app.screen_manager.screens:
                if screen.name == 'camera_screen':
                    if hasattr(screen, 'photo_captured') and screen.photo_captured:
                        screen.finish_capture()
                    else:
                        screen.cancel_capture()
                    break
    
    

class GallerySelectionState(MDBoxLayout):
    """Состояние выбора из галереи"""
    def select_test_image(self, image_num):
        """Прокси метод для выбора изображения"""
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'screen_manager'):
            for screen in app.screen_manager.screens:
                if screen.name == 'camera_screen':
                    screen.select_test_image(image_num)
                    break

class ProcessingState(MDBoxLayout):
    """Состояние обработки изображения"""
    pass

class AnalysisState(MDBoxLayout):
    """Состояние анализа нейросетью"""
    pass

class ErrorState(MDBoxLayout):
    """Состояние ошибки"""
    pass

class ResultState(MDBoxLayout):
    """Состояние показа результатов"""
    pass

class UnknownResultState(MDBoxLayout):
    """Состояние неопределенного результата"""
    pass

class CameraScreen(Screen):
    """Экран диагностики заболеваний"""
    
    # Свойства состояния
    current_state = StringProperty("source_selection")  # Текущее состояние
    photo_captured = BooleanProperty(False)  # Фото сделано
    selected_image = ObjectProperty(None)  # Выбранное изображение
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.states = {
            "source_selection": SourceSelectionState(),
            "camera_capture": CameraCaptureState(),
            "gallery_selection": GallerySelectionState(),
            "processing": ProcessingState(),
            "analysis": AnalysisState(),
            "error": ErrorState(),
            "result": ResultState(),
            "unknown": UnknownResultState()
        }
        
        # Инициализация состояния
        self.change_state("source_selection")
    
    def on_kv_post(self, base_widget):
        """Инициализация после загрузки KV"""
        super().on_kv_post(base_widget)
        self.update_action_buttons()
    
    def change_state(self, new_state):
        """Изменение текущего состояния"""
        self.current_state = new_state
        state_widget = self.states[new_state]
        
        # Очищаем основную область
        main_area = self.ids.main_area
        main_area.clear_widgets()
        main_area.add_widget(state_widget)
        
        # Обновляем кнопки действий
        self.update_action_buttons()
    
    def update_action_buttons(self):
        """Обновление кнопок действий в зависимости от состояния"""
        action_buttons = self.ids.action_buttons
        action_buttons.clear_widgets()
        
        if self.current_state == "source_selection":
            # Нет дополнительных кнопок
            pass
            
        elif self.current_state == "camera_capture":
            # Кнопки уже в состоянии
            pass
            
        elif self.current_state == "gallery_selection":
            action_buttons.add_widget(MDFlatButton(
                text="Отмена",
                on_release=lambda x: self.cancel_gallery()
            ))
            
        elif self.current_state == "processing":
            # Нет кнопок во время обработки
            pass
            
        elif self.current_state == "analysis":
            # Нет кнопок во время анализа
            pass
            
        elif self.current_state == "error":
            # Кнопки уже в состоянии
            pass
            
        elif self.current_state == "result":
            # Кнопки уже в состоянии
            pass
            
        elif self.current_state == "unknown":
            # Кнопки уже в состоянии
            pass
    
    # === Обработчики событий (заглушки) ===
    
    def use_camera(self):
        """Использовать камеру"""
        print("📷 Выбрана камера")
        self.change_state("camera_capture")
        self.photo_captured = False
    
    def use_gallery(self):
        """Использовать галерею"""
        print("🖼️ Выбрана галерея")
        self.change_state("gallery_selection")
    
    def capture_photo(self):
        """Сделать снимок (заглушка)"""
        print("📸 Снимок сделан")
        self.photo_captured = True
        
        # Обновляем кнопки в состоянии камеры
        if self.current_state == "camera_capture":
            camera_state = self.states["camera_capture"]
            if hasattr(camera_state, 'update_button_state'):
                camera_state.update_button_state(True)
            elif hasattr(camera_state, 'update_buttons'):
                camera_state.update_buttons(True)
    
    def finish_capture(self):
        """Завершить съемку и начать обработку"""
        print("✅ Съемка завершена, начинаю обработку")
        self.start_processing()
    
    def cancel_capture(self):
        """Отмена съемки"""
        print("❌ Съемка отменена")
        self.change_state("source_selection")
        self.photo_captured = False
    
    def select_test_image(self, image_num):
        """Выбрать тестовое изображение (заглушка)"""
        print(f"🖼️ Выбрано тестовое изображение {image_num}")
        self.selected_image = f"test_image_{image_num}"
        self.start_processing()
    
    def cancel_gallery(self):
        """Отмена выбора из галереи"""
        print("❌ Выбор из галереи отменен")
        self.change_state("source_selection")
    
    def start_processing(self):
        """Начать обработку изображения"""
        print("🔄 Начинаю обработку изображения")
        self.change_state("processing")
        
        # Имитация обработки с прогресс баром
        processing_state = self.states["processing"]
        Clock.schedule_interval(lambda dt: self.update_progress(dt), 0.5)
    
    def update_progress(self, dt):
        """Обновление прогресса обработки (заглушка)"""
        processing_state = self.states["processing"]
        progress_bar = processing_state.ids.progress_bar
        step_label = processing_state.ids.step_label
        
        if progress_bar.value < 100:
            progress_bar.value += 25
            step = int(progress_bar.value / 25) + 1
            step_label.text = f"Шаг {step} из 4"
            
            # Обновляем текст в зависимости от шага
            if progress_bar.value == 25:
                processing_state.ids.processing_label.text = "Загрузка изображения..."
            elif progress_bar.value == 50:
                processing_state.ids.processing_label.text = "Предобработка..."
            elif progress_bar.value == 75:
                processing_state.ids.processing_label.text = "Нормализация..."
            elif progress_bar.value == 100:
                processing_state.ids.processing_label.text = "Готово!"
                Clock.unschedule(self.update_progress)
                Clock.schedule_once(lambda dt: self.start_analysis(), 1.0)
        return True
    
    def start_analysis(self):
        """Начать анализ нейросетью"""
        print("🧠 Начинаю анализ нейросетью")
        self.change_state("analysis")
        
        # Имитация анализа
        Clock.schedule_once(lambda dt: self.finish_analysis(), 3.0)
    
    def finish_analysis(self):
        """Завершение анализа"""
        print("✅ Анализ завершен")
        
        # Случайный выбор результата для демонстрации
        import random
        result_type = random.choice(["success", "unknown", "error"])
        
        if result_type == "success":
            self.show_results()
        elif result_type == "unknown":
            self.show_unknown_result()
        else:
            self.show_error("Модель не загружена", "Не удалось загрузить модель нейросети")
    
    def show_results(self):
        """Показать результаты анализа"""
        print("📊 Показываю результаты")
        self.change_state("result")
        
        # Заглушечные данные
        result_state = self.states["result"]
        result_state.ids.result_title.text = "Заболевание обнаружено"
        result_state.ids.result_name.text = "Мучнистая роса (Erysiphales)"
        result_state.ids.result_confidence.text = "Вероятность: 87%"
        result_state.ids.recommendations.text = "• Обработать фунгицидом 'Скор'\n• Удалить пораженные листья\n• Обеспечить хорошую вентиляцию\n• Избегать избыточного полива"
        result_state.ids.pesticides.text = "• Скор (0.2 л/га)\n• Топаз (0.1 л/га)\n• Фундазол (0.5 кг/га)\n• Квадрис (0.6 л/га)"
    
    def show_unknown_result(self):
        """Показать неопределенный результат"""
        print("❓ Результат не определен")
        self.change_state("unknown")
    
    def show_error(self, title, message):
        """Показать ошибку"""
        print(f"❌ Ошибка: {title} - {message}")
        self.change_state("error")
        
        error_state = self.states["error"]
        error_state.ids.error_title.text = title
        error_state.ids.error_message.text = message
    
    # === Обработчики кнопок результатов ===
    
    def open_catalog(self):
        """Открыть каталог препаратов"""
        print("📚 Открываю каталог препаратов")
        # Здесь будет переход в каталог
        self.show_message("Переход в каталог", "Функция будет реализована позже")
    
    def reset_analysis(self):
        """Сбросить анализ и начать заново"""
        print("🔄 Сбрасываю анализ")
        self.change_state("source_selection")
        self.photo_captured = False
        self.selected_image = None
    
    def retry_analysis(self):
        """Повторить анализ"""
        print("🔄 Повторяю анализ")
        self.start_processing()
    
    def back_to_start(self):
        """Вернуться к началу"""
        print("🏠 Возвращаюсь к началу")
        self.change_state("source_selection")
        
    def show_help(self):
        """Показать справку"""
        print("❓ Показываю справку")
        dialog = MDDialog(
            title="Справка по диагностике",
            text="1. Выберите источник изображения (камера или галерея)\n\n2. Сделайте четкий снимок пораженного растения\n\n3. Дождитесь обработки и анализа изображения\n\n4. Просмотрите результаты и рекомендации\n\n5. Используйте кнопку 'Открыть каталог' для подбора препаратов",
            size_hint=(0.8, 0.6)
        )
        dialog.open()
    
    def show_message(self, title, message):
        """Показать информационное сообщение"""
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()