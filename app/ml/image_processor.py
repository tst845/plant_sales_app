import cv2
import numpy as np
from PIL import Image

class ImageProcessor:
    """Класс для обработки изображений перед подачей в нейросеть"""
    
    @staticmethod
    def preprocess_image(image_path, target_size=(224, 224)):
        """Предобработка изображения для нейросети"""
        try:
            # Загрузка изображения
            image = Image.open(image_path)
            image = image.convert('RGB')
            
            # Изменение размера
            image = image.resize(target_size)
            
            # Конвертация в numpy array и нормализация
            image_array = np.array(image) / 255.0
            
            # Добавление batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            print(f"Ошибка обработки изображения: {e}")
            return None
    
    @staticmethod
    def load_and_preprocess_from_bytes(image_bytes, target_size=(224, 224)):
        """Загрузка и предобработка изображения из bytes"""
        try:
            # Конвертация bytes в numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Изменение размера
            image = cv2.resize(image, target_size)
            
            # Нормализация
            image = image / 255.0
            
            # Добавление batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            print(f"Ошибка обработки изображения из bytes: {e}")
            return None