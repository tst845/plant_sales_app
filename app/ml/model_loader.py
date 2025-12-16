import tensorflow as tf
import numpy as np

class ModelLoader:
    """Класс для загрузки и использования моделей TensorFlow Lite"""
    
    def __init__(self):
        self.model = None
        self.input_details = None
        self.output_details = None
    
    def load_model(self, model_path):
        """Загрузка модели TFLite"""
        try:
            # Загрузка модели
            self.model = tf.lite.Interpreter(model_path=model_path)
            self.model.allocate_tensors()
            
            # Получение информации о входе и выходе
            self.input_details = self.model.get_input_details()
            self.output_details = self.model.get_output_details()
            
            print("✅ Модель успешно загружена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            return False
    
    def predict(self, input_data):
        """Выполнение предсказания на входных данных"""
        try:
            if self.model is None:
                raise ValueError("Модель не загружена")
            
            # Установка входных данных
            self.model.set_tensor(self.input_details[0]['index'], input_data.astype(np.float32))
            
            # Выполнение инференса
            self.model.invoke()
            
            # Получение результатов
            output_data = self.model.get_tensor(self.output_details[0]['index'])
            
            return output_data
            
        except Exception as e:
            print(f"❌ Ошибка предсказания: {e}")
            return None
    
    def get_top_predictions(self, predictions, top_k=3):
        """Получение топ-K предсказаний"""
        try:
            # Получение индексов топ-K предсказаний
            top_indices = np.argsort(predictions[0])[-top_k:][::-1]
            top_probabilities = predictions[0][top_indices]
            
            return list(zip(top_indices, top_probabilities))
            
        except Exception as e:
            print(f"❌ Ошибка получения топ предсказаний: {e}")
            return []