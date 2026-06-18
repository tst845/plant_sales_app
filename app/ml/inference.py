import onnxruntime as ort
import numpy as np
from PIL import Image
from pathlib import Path
from kivy.clock import Clock
from kivy.app import App

# ================== СЛОВАРИ КЛАССОВ ==================
idx_to_species = {
    0: 'Apple', 1: 'Bell_pepper', 2: 'Cherry', 3: 'Corn',
    4: 'Grape', 5: 'Peach', 6: 'Potato', 7: 'Squash',
    8: 'Strawberry', 9: 'Tomato', 10: 'unknown_object', 11: 'unknown_plant'
}
idx_to_disease = {
    0: 'alternaria_leaf_spot_apple',
    1: 'apple scab',
    2: 'bacterial_spot_peach',
    3: 'bacterial_spot_pepper',
    4: 'bacterial_spot_tomato',
    5: 'black rot',
    6: 'brown_spot_apple',
    7: 'cedar_apple_rust',
    8: 'common_rust_corn',
    9: 'early blight',
    10: 'esca (black measles)',
    11: 'gray_leaf_spot_corn',
    12: 'gray_spot_apple',
    13: 'healthy',
    14: 'late blight',
    15: 'leaf blight (isariopsis leaf spot)',
    16: 'leaf scorch',
    17: 'leaf_mold_tomato',
    18: 'northern_leaf_blight_corn',
    19: 'powdery_mildew',
    20: 'scab',
    21: 'septoria_leaf_spot_tomato',
    22: 'spider mites two-spotted spider mite',
    23: 'target spot',
    24: 'tomato yellow leaf curl virus',
    25: 'tomato_mosaic_virus',
    26: 'unknown'
}

# Русские названия для отображения
species_ru = {
    0: 'Яблоня',
    1: 'Сладкий перец',
    2: 'Вишня',
    3: 'Кукуруза',
    4: 'Виноград',
    5: 'Персик',
    6: 'Картофель',
    7: 'Тыква',
    8: 'Клубника',
    9: 'Томат',
    10: 'Неизвестный объект',
    11: 'Неизвестное растение'
}

disease_ru = {
    0: 'Альтернариоз яблони',
    1: 'Парша яблони',
    2: 'Бактериальная пятнистость персика',
    3: 'Бактериальная пятнистость перца',
    4: 'Бактериальная пятнистость томата',
    5: 'Чёрная гниль',
    6: 'Бурая пятнистость яблони',
    7: 'Ржавчина можжевельника-яблони',
    8: 'Обычная ржавчина кукурузы',
    9: 'Фитофтороз ранний',
    10: 'Эска (чёрная пятнистость)',
    11: 'Серая листовая пятнистость кукурузы',
    12: 'Серая пятнистость яблони',
    13: 'Здоровое растение',
    14: 'Фитофтороз поздний',
    15: 'Листовая пятнистость (изариопсис)',
    16: 'Листовой ожог',
    17: 'Листовая плесень томата',
    18: 'Северная листовая пятнистость кукурузы',
    19: 'Мучнистая роса',
    20: 'Парша',
    21: 'Септориоз томата',
    22: 'Паутинный клещ',
    23: 'Целевая пятнистость',
    24: 'Вирус желтой курчавости листьев томата',
    25: 'Вирус мозаики томата',
    26: 'Неизвестно'
}

THRESHOLD = 0.9

class PlantModel:
    def __init__(self):
        self.seg_sess = None
        self.cls_sess = None
        self.loaded = False

    def load_models(self):
        """Загрузить ONNX модели из папки assets"""
        try:
            base_dir = Path(__file__).parent.parent.parent
            models_dir = base_dir / "app" / "assets" / "models"
            seg_path = models_dir / "segmentation_model.onnx"
            cls_path = models_dir / "model_classifier.onnx"
            
            self.seg_sess = ort.InferenceSession(str(seg_path))
            self.cls_sess = ort.InferenceSession(str(cls_path))
            self.loaded = True
            print(" Модели ONNX загружены")
            return True
        except Exception as e:
            print(f" Ошибка загрузки моделей: {e}")
            self.loaded = False
            return False

    def _resize_and_normalize(self, img_pil, size=(512, 512), mean=None, std=None):
        """Изменяет размер и нормализует изображение (HWC -> CHW)"""
        img = img_pil.resize(size, Image.BILINEAR)
        img_np = np.array(img, dtype=np.float32) / 255.0
        if mean is not None and std is not None:
            img_np = (img_np - mean) / std
        # CHW
        img_np = img_np.transpose((2, 0, 1))
        return img_np

    def preprocess_segmentation(self, image_path):
        """Подготовка изображения для сегментационной модели (без torchvision)"""
        # Статистика ImageNet
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img_pil = Image.open(image_path).convert('RGB')
        img_tensor = self._resize_and_normalize(img_pil, size=(512, 512), mean=mean, std=std)
        img_tensor = np.expand_dims(img_tensor, axis=0)  # (1,3,512,512)
        return img_pil, img_tensor

    def preprocess_classification(self, img_pil, leaf_mask, disease_mask):
        """Подготовка 5-канального входа для классификатора"""
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        # RGB каналы (нормализованные, CHW)
        rgb_np = self._resize_and_normalize(img_pil, size=(512, 512), mean=mean, std=std)  # (3,512,512)
        # Маски: (512,512) -> (1,512,512)
        leaf_mask_np = leaf_mask[np.newaxis, :, :]
        disease_mask_np = disease_mask[np.newaxis, :, :]
        # Конкатенация по каналам -> (5,512,512)
        input_cls = np.concatenate([rgb_np, leaf_mask_np, disease_mask_np], axis=0)
        input_cls = np.expand_dims(input_cls, axis=0).astype(np.float32)  # (1,5,512,512)
        return input_cls

    def create_masked_image(self, image_path, leaf_mask, disease_mask):
        """Наложить полупрозрачные маски на изображение и сохранить в PNG"""
        img = Image.open(image_path).convert('RGB')
        img = img.resize((512, 512), Image.BILINEAR)
        img_np = np.array(img).astype(np.float32) / 255.0  # (512,512,3)

        # Результат начинаем с копии оригинала
        result = img_np.copy()

        # Настройки прозрачности (0.0 = полностью прозрачно, 1.0 = непрозрачно)
        leaf_alpha = 0.5      # зелёная маска листа
        disease_alpha = 0.5   # красная маска болезни

        # Маска листа (зелёный цвет)
        leaf_overlay = np.zeros_like(result)
        leaf_overlay[:, :, 1] = leaf_mask   # зелёный канал
        alpha = leaf_alpha * leaf_mask[:, :, np.newaxis]
        result = result * (1 - alpha) + leaf_overlay * alpha

        # Маска болезни (красный цвет)
        disease_overlay = np.zeros_like(result)
        disease_overlay[:, :, 0] = disease_mask   # красный канал
        alpha = disease_alpha * disease_mask[:, :, np.newaxis]
        result = result * (1 - alpha) + disease_overlay * alpha

        result = np.clip(result, 0, 1)
        result = (result * 255).astype(np.uint8)

        # Сохраняем как PNG (поддерживает прозрачность, но здесь она не нужна)
        temp_path = Path(image_path).parent / f"masked_{Path(image_path).stem}.png"
        Image.fromarray(result).save(temp_path, format='PNG')
        return str(temp_path)

    def predict(self, image_path, progress_callback=None):
        """Выполнить полный пайплайн: сегментация -> классификация"""
        if not self.loaded:
            raise RuntimeError("Модели не загружены. ")

        if progress_callback:
            progress_callback(0.1)
        img_pil, seg_input = self.preprocess_segmentation(image_path)
        leaf_prob, disease_prob = self.seg_sess.run(None, {"input_rgb": seg_input})
        leaf_mask = leaf_prob[0, 0, :, :]      # (512,512)
        disease_mask = disease_prob[0, 0, :, :]

        masked_path = self.create_masked_image(image_path, leaf_mask, disease_mask)

        if progress_callback:
            progress_callback(0.5)

        cls_input = self.preprocess_classification(img_pil, leaf_mask, disease_mask)
        species_logits, disease_logits = self.cls_sess.run(None, {"input": cls_input})

        if progress_callback:
            progress_callback(0.9)

        # Softmax
        def softmax(x):
            ex = np.exp(x - np.max(x, axis=1, keepdims=True))
            return ex / np.sum(ex, axis=1, keepdims=True)

        species_probs = softmax(species_logits)
        disease_probs = softmax(disease_logits)

        species_top1 = np.argmax(species_probs[0])
        species_conf = species_probs[0, species_top1]
        disease_top1 = np.argmax(disease_probs[0])
        disease_conf = disease_probs[0, disease_top1]
        
        # ==== русскоязычные названия из локального кода 
        species_text_ru = species_ru.get(species_top1, idx_to_species[species_top1])
        # Формирование текста по пороговой логике
        if species_conf >= THRESHOLD:
            # species_text = f"{idx_to_species[species_top1]} ({species_conf:.3f})"
            species_text = f"{species_text_ru} ({species_conf:.3f})"
        else:
            top3_idx = np.argsort(species_probs[0])[::-1][:3]
            # top3 = [f"{idx_to_species[i]}: {species_probs[0,i]:.3f}" for i in top3_idx]
            top3 = [f"{species_ru.get(i, idx_to_species[i])}: {species_probs[0,i]:.3f}" for i in top3_idx]
            species_text = "не уверен, возможные варианты:\n" + "\n".join(top3)

        disease_text_ru = disease_ru.get(disease_top1, idx_to_disease[disease_top1])
        if disease_conf >= THRESHOLD:
            # disease_text = f"{idx_to_disease[disease_top1]} ({disease_conf:.3f})"
            disease_text = f"{disease_text_ru} ({disease_conf:.3f})"
        else:
            top3_idx = np.argsort(disease_probs[0])[::-1][:3]
            # top3 = [f"{idx_to_disease[i]}: {disease_probs[0,i]:.3f}" for i in top3_idx]
            top3 = [f"{disease_ru.get(i, idx_to_disease[i])}: {disease_probs[0,i]:.3f}" for i in top3_idx]
            disease_text = "не уверен, возможные варианты:\n" + "\n".join(top3)

        if progress_callback:
            progress_callback(1.0)

        return {
            "species": species_text,
            "disease": disease_text,
            "species_conf": float(species_conf),
            "disease_conf": float(disease_conf),
            "species_idx": int(species_top1),
            "disease_idx": int(disease_top1),
            "masked_image_path": masked_path,
            "species_probs": species_probs[0].tolist(),
            "disease_probs": disease_probs[0].tolist()
        }