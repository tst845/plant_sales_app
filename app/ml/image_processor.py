import io
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
        """Загрузка и предобработка изображения из bytes (без OpenCV)"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert('RGB')
            image = image.resize(target_size)
            image_array = np.array(image) / 255.0
            image_array = np.expand_dims(image_array, axis=0)
            return image_array
        except Exception as e:
            print(f"Ошибка обработки изображения из bytes: {e}")
            return None