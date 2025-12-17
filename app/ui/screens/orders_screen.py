# app/ui/screens/orders_screen.py

from kivy.lang import Builder
from kivy.properties import StringProperty, DictProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp

import datetime

Builder.load_string("""
<OrdersTab>:
    name: "orders"
    text: "Заказы"
    icon: "cart"
    
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        padding: dp(10)
        
        MDTopAppBar:
            title: "Заказы"
            elevation: 4
            left_action_items: [["refresh", lambda x: root.refresh_orders()]]
            right_action_items: [["plus", lambda x: root.create_new_order()]]
        
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            
            MDLabel:
                text: "Список заказов"
                font_style: "H6"
                size_hint_y: None
                height: dp(40)
            
            ScrollView:
                MDList:
                    id: orders_list
                    spacing: dp(10)
""")

class OrderItemCard(MDCard):
    """Карточка позиции в заказе"""
    
    def __init__(self, order_item, **kwargs):
        super().__init__(**kwargs)
        self.order_item = order_item
        self.size_hint_y = None
        self.height = dp(100)
        self.padding = dp(10)
        self.spacing = dp(10)
        
        layout = MDBoxLayout(orientation="horizontal", spacing=dp(10))
        
        # Информация о препарате
        info_layout = MDBoxLayout(orientation="vertical", size_hint_x=0.7)
        info_layout.add_widget(MDLabel(
            text=f"{order_item.get('name', 'Неизвестный препарат')}",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        ))
        info_layout.add_widget(MDLabel(
            text=f"Кол-во: {order_item.get('quantity', 1)} × {order_item.get('price', 0)} ₽",
            font_style="Body1"
        ))
        info_layout.add_widget(MDLabel(
            text=f"Сумма: {order_item.get('total', 0)} ₽",
            font_style="Body1",
            theme_text_color="Secondary"
        ))
        
        # Кнопки управления
        button_layout = MDBoxLayout(orientation="vertical", size_hint_x=0.3)
        edit_btn = MDFlatButton(
            text="Изменить",
            on_release=lambda x: self.edit_item()
        )
        delete_btn = MDFlatButton(
            text="Удалить",
            on_release=lambda x: self.delete_item()
        )
        button_layout.add_widget(edit_btn)
        button_layout.add_widget(delete_btn)
        
        layout.add_widget(info_layout)
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def edit_item(self):
        """Редактировать позицию"""
        pass
    
    def delete_item(self):
        """Удалить позицию"""
        pass

class CustomerSelectionDialog(MDDialog):
    """Диалог выбора клиента"""
    
    def __init__(self, callback, **kwargs):
        super().__init__(
            title="Выбор клиента",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(400)
            ),
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dismiss()),
                MDRaisedButton(text="Выбрать", on_release=lambda x: self.select_customer())
            ],
            **kwargs
        )
        self.callback = callback
        self.selected_customer = None
        
        # Поле поиска
        self.search_field = MDTextField(
            hint_text="Поиск клиента...",
            size_hint_y=None,
            height=dp(50)
        )
        self.content_cls.add_widget(self.search_field)
        
        # Список клиентов
        self.customers_list = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None
        )
        self.customers_list.bind(minimum_height=self.customers_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.customers_list)
        self.content_cls.add_widget(scroll)
        
        # Загрузка тестовых клиентов
        self.load_test_customers()
    
    def load_test_customers(self):
        """Загрузка тестовых данных клиентов"""
        test_customers = [
            {"id": 1, "name": "ООО 'АгроПром'", "inn": "1234567890"},
            {"id": 2, "name": "ИП Иванов", "inn": "0987654321"},
            {"id": 3, "name": "Фермерское хозяйство 'Рассвет'", "inn": "1122334455"},
            {"id": 4, "name": "Сельхозкооператив 'Нива'", "inn": "5566778899"},
        ]
        
        for customer in test_customers:
            item = OneLineListItem(
                text=f"{customer['name']} (ИНН: {customer['inn']})",
                on_release=lambda x, c=customer: self.select_customer_item(c)
            )
            self.customers_list.add_widget(item)
    
    def select_customer_item(self, customer):
        """Выбор клиента из списка"""
        self.selected_customer = customer
        # Подсветка выбранного
        for child in self.customers_list.children:
            if isinstance(child, OneLineListItem):
                if child.text.startswith(customer['name']):
                    child.bg_color = (0.9, 0.9, 0.9, 1)  # Подсветка серым
    
    def select_customer(self):
        """Подтверждение выбора клиента"""
        if self.selected_customer:
            self.callback(self.selected_customer)
        self.dismiss()

class ProductSelectionDialog(MDDialog):
    """Диалог выбора препарата"""
    
    def __init__(self, callback, **kwargs):
        super().__init__(
            title="Выбор препарата",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(500)
            ),
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dismiss()),
                MDRaisedButton(text="Добавить", on_release=lambda x: self.select_product())
            ],
            **kwargs
        )
        self.callback = callback
        self.selected_product = None
        
        # Поле поиска
        self.search_field = MDTextField(
            hint_text="Поиск препарата...",
            size_hint_y=None,
            height=dp(50)
        )
        self.content_cls.add_widget(self.search_field)
        
        # Список препаратов
        self.products_list = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None
        )
        self.products_list.bind(minimum_height=self.products_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.products_list)
        self.content_cls.add_widget(scroll)
        
        # Загрузка тестовых препаратов
        self.load_test_products()
    
    def load_test_products(self):
        """Загрузка тестовых данных препаратов"""
        test_products = [
            {"id": 1, "name": "Гербицид 'Раундап'", "price": 1500, "unit": "л"},
            {"id": 2, "name": "Инсектицид 'Актара'", "price": 2500, "unit": "кг"},
            {"id": 3, "name": "Фунгицид 'Скор'", "price": 1800, "unit": "л"},
            {"id": 4, "name": "Удобрение 'Азофоска'", "price": 1200, "unit": "кг"},
        ]
        
        for product in test_products:
            item = TwoLineListItem(
                text=product['name'],
                secondary_text=f"Цена: {product['price']} ₽/{product['unit']}",
                on_release=lambda x, p=product: self.select_product_item(p)
            )
            self.products_list.add_widget(item)
    
    def select_product_item(self, product):
        """Выбор препарата из списка"""
        self.selected_product = product
        # Подсветка выбранного
        for child in self.products_list.children:
            if isinstance(child, TwoLineListItem):
                if child.text == product['name']:
                    child.bg_color = (0.9, 0.9, 0.9, 1)  # Подсветка серым
    
    def select_product(self):
        """Подтверждение выбора препарата"""
        if self.selected_product:
            self.callback(self.selected_product)
        self.dismiss()

class OrderConfirmationDialog(MDDialog):
    """Диалог подтверждения заказа"""
    
    def __init__(self, order_data, confirm_callback, **kwargs):
        super().__init__(
            title="Подтверждение заказа",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(300)
            ),
            buttons=[
                MDFlatButton(text="Назад", on_release=lambda x: self.dismiss()),
                MDRaisedButton(text="Подтвердить", on_release=lambda x: self.confirm_order())
            ],
            **kwargs
        )
        self.order_data = order_data
        self.confirm_callback = confirm_callback
        
        # Информация о заказе
        self.content_cls.add_widget(MDLabel(
            text=f"Клиент: {order_data.get('customer_name', 'Не выбран')}",
            font_style="H6"
        ))
        
        self.content_cls.add_widget(MDLabel(
            text=f"Количество позиций: {len(order_data.get('items', []))}",
            font_style="Body1"
        ))
        
        self.content_cls.add_widget(MDLabel(
            text=f"Общая сумма: {order_data.get('total_amount', 0)} ₽",
            font_style="H5",
            theme_text_color="Secondary"
        ))
    
    def confirm_order(self):
        """Подтверждение заказа"""
        self.confirm_callback(self.order_data)
        self.dismiss()

class OrdersTab(MDBottomNavigationItem):
    """Вкладка заказов"""
    
    current_order = DictProperty()
    order_state = StringProperty("list")  # list, draft, items, confirm
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_order = {
            "id": None,
            "customer": None,
            "items": [],
            "total_amount": 0,
            "status": "draft",
            "created_at": None
        }
        
    def on_enter(self):
        """Вызывается при переходе на вкладку"""
        self.refresh_orders()
    
    def refresh_orders(self):
        """Обновление списка заказов"""
        orders_list = self.ids.orders_list
        orders_list.clear_widgets()
        
        # Тестовые данные
        test_orders = [
            {"id": 1, "customer": "ООО 'АгроПром'", "amount": 45000, "status": "completed", "date": "2025-12-01"},
            {"id": 2, "customer": "ИП Иванов", "amount": 23000, "status": "processing", "date": "2025-12-05"},
            {"id": 3, "customer": "Фермерское хозяйство 'Рассвет'", "amount": 0, "status": "draft", "date": "2025-12-07"},
        ]
        
        for order in test_orders:
            status_colors = {
                "draft": (1, 0.65, 0, 0.3),  # Orange с прозрачностью
                "processing": (0.68, 0.85, 0.9, 0.3),  # Blue с прозрачностью
                "completed": (0.68, 0.93, 0.68, 0.3)   # Green с прозрачностью
            }
            
            item = ThreeLineListItem(
                text=f"Заказ #{order['id']}",
                secondary_text=f"Клиент: {order['customer']}",
                tertiary_text=f"Сумма: {order['amount']} ₽ | Статус: {order['status']} | {order['date']}",
                bg_color=status_colors.get(order['status'], (1, 1, 1, 1)),
                on_release=lambda x, o=order: self.open_order(o)
            )
            orders_list.add_widget(item)
    
    def create_new_order(self):
        """Создание нового заказа"""
        self.current_order = {
            "id": None,
            "customer": None,
            "items": [],
            "total_amount": 0,
            "status": "draft",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.order_state = "draft"
        self.show_customer_selection()
    
    def open_order(self, order):
        """Открытие существующего заказа"""
        if order['status'] == 'draft':
            self.current_order = order.copy()
            # Добавляем поле customer_name для совместимости
            self.current_order['customer_name'] = order['customer']
            self.order_state = "draft"
            self.show_customer_selection()
        else:
            self.show_order_details(order)
    
    def show_customer_selection(self):
        """Показать диалог выбора клиента"""
        dialog = CustomerSelectionDialog(
            callback=self.on_customer_selected
        )
        dialog.open()
    
    def on_customer_selected(self, customer):
        """Обработка выбора клиента"""
        self.current_order['customer'] = customer
        self.current_order['customer_name'] = customer['name']
        self.show_order_items()
    
    def show_order_items(self):
        """Показать экран добавления позиций"""
        self.order_state = "items"
        self.show_items_dialog()
    
    def show_items_dialog(self):
        """Диалог управления позициями заказа"""
        dialog = MDDialog(
            title=f"Позиции заказа (Клиент: {self.current_order.get('customer_name', 'Не выбран')})",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(500)
            ),
            buttons=[
                MDFlatButton(text="Назад", on_release=lambda x: self.back_to_customer()),
                MDFlatButton(text="Добавить позицию", on_release=lambda x: self.add_order_item()),
                MDRaisedButton(text="Далее", on_release=lambda x: self.show_confirmation())
            ]
        )
        
        # Список позиций
        items_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )
        items_layout.bind(minimum_height=items_layout.setter('height'))
        
        if self.current_order['items']:
            for item in self.current_order['items']:
                card = OrderItemCard(item)
                items_layout.add_widget(card)
        else:
            items_layout.add_widget(MDLabel(
                text="Позиции не добавлены",
                halign="center",
                theme_text_color="Secondary"
            ))
        
        scroll = ScrollView()
        scroll.add_widget(items_layout)
        dialog.content_cls.add_widget(scroll)
        
        # Итоговая сумма
        dialog.content_cls.add_widget(MDLabel(
            text=f"Итого: {self.calculate_total()} ₽",
            font_style="H5",
            size_hint_y=None,
            height=dp(40),
            halign="right"
        ))
        
        self.items_dialog = dialog
        dialog.open()
    
    def add_order_item(self):
        """Добавление новой позиции"""
        dialog = ProductSelectionDialog(
            callback=self.on_product_selected
        )
        dialog.open()
    
    def on_product_selected(self, product):
        """Обработка выбора препарата"""
        # Добавляем тестовую позицию
        new_item = {
            "id": len(self.current_order['items']) + 1,
            "product_id": product['id'],
            "name": product['name'],
            "quantity": 1,
            "price": product['price'],
            "unit": product['unit'],
            "total": product['price']
        }
        
        self.current_order['items'].append(new_item)
        self.current_order['total_amount'] = self.calculate_total()
        
        if hasattr(self, 'items_dialog') and self.items_dialog:
            self.items_dialog.dismiss()
        
        self.show_items_dialog()
    
    def calculate_total(self):
        """Расчет общей суммы заказа"""
        total = 0
        for item in self.current_order['items']:
            total += item.get('total', 0)
        return total
    
    def show_confirmation(self):
        """Показать диалог подтверждения"""
        if hasattr(self, 'items_dialog') and self.items_dialog:
            self.items_dialog.dismiss()
        
        dialog = OrderConfirmationDialog(
            order_data=self.current_order,
            confirm_callback=self.confirm_order
        )
        dialog.open()
    
    def back_to_customer(self):
        """Вернуться к выбору клиента"""
        if hasattr(self, 'items_dialog') and self.items_dialog:
            self.items_dialog.dismiss()
        
        self.show_customer_selection()
    
    def confirm_order(self, order_data):
        """Подтверждение заказа"""
        # Здесь будет логика сохранения заказа в БД
        print(f"Заказ подтвержден: {order_data}")
        self.order_state = "completed"
        self.show_order_completed()
    
    def show_order_completed(self):
        """Показать экран завершения заказа"""
        dialog = MDDialog(
            title="Заказ оформлен!",
            text=f"Заказ #{self.current_order.get('id', 'новый')} успешно оформлен.\nСумма: {self.current_order['total_amount']} ₽",
            buttons=[
                MDFlatButton(text="Экспорт КП", on_release=lambda x: self.export_to_pdf()),
                MDRaisedButton(text="Готово", on_release=lambda x: self.finish_order())
            ]
        )
        dialog.open()
    
    def export_to_pdf(self):
        """Экспорт коммерческого предложения в PDF"""
        # Заглушка для экспорта
        print("Экспорт КП в PDF...")
        # Здесь будет логика генерации PDF
    
    def finish_order(self):
        """Завершение работы с заказом"""
        self.order_state = "list"
        self.refresh_orders()
    
    def show_order_details(self, order):
        """Показать детали завершенного заказа"""
        dialog = MDDialog(
            title=f"Заказ #{order['id']}",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(300)
            ),
            buttons=[
                MDFlatButton(text="Закрыть", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Экспорт КП", on_release=lambda x: self.export_order_pdf(order))
            ]
        )
        
        dialog.content_cls.add_widget(MDLabel(
            text=f"Клиент: {order['customer']}",
            font_style="H6"
        ))
        
        dialog.content_cls.add_widget(MDLabel(
            text=f"Статус: {order['status']}",
            font_style="Body1"
        ))
        
        dialog.content_cls.add_widget(MDLabel(
            text=f"Сумма: {order['amount']} ₽",
            font_style="H5",
            theme_text_color="Secondary"
        ))
        
        dialog.content_cls.add_widget(MDLabel(
            text=f"Дата: {order['date']}",
            font_style="Body1",
            theme_text_color="Secondary"
        ))
        
        dialog.open()
    
    def export_order_pdf(self, order):
        """Экспорт конкретного заказа в PDF"""
        print(f"Экспорт заказа #{order['id']} в PDF...")
        # Здесь будет логика генерации PDF для конкретного заказа