import os
from pathlib import Path

class AppConfig:
    """Конфигурация приложения"""
    
    def __init__(self):
        self.app_name = "Plant Protection"
        self.version = "1.0.0"
        
        # Пути к ресурсам
        self.base_dir = Path(__file__).parent.parent.parent
        self.assets_dir = self.base_dir / "app" / "assets"
        self.models_dir = self.assets_dir / "models"
        self.database_dir = self.assets_dir / "database"
        
        # Настройки базы данных
        self.database_path = self.database_dir / "plant_protection.db"
        
        # Создание директорий если не существуют
        self._create_directories()
    
    def _create_directories(self):
        """Создание необходимых директорий"""
        directories = [
            self.assets_dir,
            self.models_dir,
            self.database_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)