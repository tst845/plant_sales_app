import os
import ast
import pathlib
import argparse
from datetime import datetime
from typing import Set, List, Dict, Optional
import re

class SmartProjectExporter:
    """
    !!! Обрезает файлы, нет экспорта БД!!!
    Умный экспорт проекта с зависимостями.
    Экспортирует структуру, целевой файл и все его зависимости.
    """
    
    def __init__(self, root_path="."):
        self.root_path = pathlib.Path(root_path).resolve()
        
        # Директории для исключения
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
            'venv', '.venv', 'env', '.env', 'envs',
            '.vscode', '.idea', 'vs_code',
            'dist', 'build', '*.egg-info',
            'node_modules', 'coverage', '.coverage',
            '.github', '.gitlab', '.bitbucket',
            'generated_docs'  # исключаем документацию
        }
        
        # Файлы для исключения
        self.exclude_files = {
            '*.pyc', '*.pyo', '*.pyd', '*.so',
            '*.db', '*.sqlite', '*.sqlite3', '*.log',
            'poetry.lock', 'package-lock.json', 'yarn.lock',
            '.gitignore', '.env', '.env.local', '.env.*',
            'Thumbs.db', 'desktop.ini', '.DS_Store'
        }
        
        self.import_graph: Dict[str, Set[str]] = {}
        self.analyzed_files: Set[str] = set()
        
    def should_skip(self, path: pathlib.Path) -> bool:
        """Определить, нужно ли пропустить файл/папку"""
        name = path.name
        
        # Пропускаем скрытые файлы
        if name.startswith('.'):
            return True
        
        # Пропускаем исключенные директории
        if path.is_dir():
            for pattern in self.exclude_dirs:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern:
                    return True
        
        # Пропускаем файлы в исключенных директориях
        for parent in path.parents:
            if parent.name in self.exclude_dirs:
                return True
        
        # Пропускаем исключенные файлы по шаблону
        if path.is_file():
            for pattern in self.exclude_files:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern:
                    return True
        
        return False
    
    def analyze_imports(self, file_path: pathlib.Path) -> Set[str]:
        """Анализирует импорты в файле и возвращает зависимости"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Стандартные импорты
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])  # Берем только модуль
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # from module import ...
                        imports.add(node.module.split('.')[0])
                    # from . import something
                    elif node.level > 0:  # Относительный импорт
                        # Находим локальный модуль
                        current_dir = file_path.parent
                        for i in range(node.level - 1):
                            current_dir = current_dir.parent
                        # Ищем файлы с импортируемыми именами
                        for name_obj in node.names:
                            # Пытаемся найти файл
                            possible_names = [
                                f"{name_obj.name}.py",
                                f"{name_obj.name}/__init__.py"
                            ]
                            for possible in possible_names:
                                possible_path = current_dir / possible
                                if possible_path.exists():
                                    rel_path = possible_path.relative_to(self.root_path)
                                    imports.add(str(rel_path).replace('.py', '').replace('/', '.'))
            
            # Анализ строковых импортов (для Kivy, SQLAlchemy и т.д.)
            string_imports = re.findall(r"from\s+['\"](.+?)['\"]", content)
            string_imports += re.findall(r"import\s+['\"](.+?)['\"]", content)
            
            for imp in string_imports:
                imports.add(imp.split('.')[0])
                
        except Exception as e:
            print(f"⚠️  Ошибка анализа {file_path}: {e}")
        
        return imports
    
    def find_dependencies(self, target_file: pathlib.Path) -> Set[pathlib.Path]:
        """Находит все зависимости для целевого файла"""
        all_deps = set()
        to_analyze = {target_file}
        
        print(f"🔍 Поиск зависимостей для {target_file.name}...")
        
        while to_analyze:
            current_file = to_analyze.pop()
            
            if current_file in self.analyzed_files:
                continue
                
            self.analyzed_files.add(current_file)
            
            if not current_file.exists():
                print(f"⚠️  Файл не найден: {current_file}")
                continue
            
            # Анализируем импорты
            imports = self.analyze_imports(current_file)
            self.import_graph[str(current_file.relative_to(self.root_path))] = imports
            
            # Находим файлы для найденных импортов
            for imp in imports:
                found_files = self.find_file_by_import(imp, current_file.parent)
                for found_file in found_files:
                    if found_file not in self.analyzed_files:
                        to_analyze.add(found_file)
                        all_deps.add(found_file)
            
            # Специальные зависимости для типичных структур
            self._add_special_dependencies(current_file, all_deps, to_analyze)
        
        return all_deps
    
    def find_file_by_import(self, import_name: str, search_from: pathlib.Path) -> List[pathlib.Path]:
        """Находит файл по имени импорта"""
        found_files = []
        
        # Пробуем разные варианты
        possible_paths = [
            # Прямой путь из корня проекта
            self.root_path / import_name.replace('.', '/') / '__init__.py',
            self.root_path / f"{import_name.replace('.', '/')}.py",
            
            # Относительно текущего файла
            search_from / f"{import_name}.py",
            search_from / import_name / '__init__.py',
            
            # Для app.module
            self.root_path / 'app' / import_name.replace('.', '/') / '__init__.py',
            self.root_path / 'app' / f"{import_name.replace('.', '/')}.py",
        ]
        
        # Рекурсивный поиск
        for pattern in [f"**/{import_name}.py", f"**/{import_name}/__init__.py"]:
            try:
                for found in self.root_path.glob(pattern):
                    if not self.should_skip(found):
                        found_files.append(found)
            except Exception:
                pass
        
        # Убираем дубликаты и проверяем существование
        unique_files = []
        for file in found_files:
            if file.exists() and file not in unique_files:
                unique_files.append(file)
        
        return unique_files
    
    def _add_special_dependencies(self, current_file: pathlib.Path, 
                                  all_deps: Set[pathlib.Path], 
                                  to_analyze: Set[pathlib.Path]):
        """Добавляет специальные зависимости на основе содержимого файла"""
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            current_rel = str(current_file.relative_to(self.root_path))
            
            # Для файлов с "database" в имени
            if 'database' in current_file.name.lower():
                # Ищем связанные конфиги
                for pattern in ['**/config.py', '**/configs.py', '**/settings.py']:
                    for config_file in self.root_path.glob(pattern):
                        if not self.should_skip(config_file) and config_file not in all_deps:
                            all_deps.add(config_file)
                            to_analyze.add(config_file)
            
            # Для UI файлов
            if any(x in current_rel for x in ['screen', 'widget', 'ui']):
                # Ищем связанные виджеты
                for pattern in ['**/widgets/**/*.py', '**/ui/**/*.py']:
                    for ui_file in self.root_path.glob(pattern):
                        if not self.should_skip(ui_file) and ui_file != current_file:
                            # Проверяем, упоминается ли в коде
                            try:
                                with open(ui_file, 'r', encoding='utf-8') as f_ui:
                                    ui_content = f_ui.read()
                                ui_name = ui_file.stem
                                if ui_name in content or ui_name in current_rel:
                                    all_deps.add(ui_file)
                            except:
                                pass
                
                # Проверяем ссылки на главные файлы
                main_files = ['main.py', 'app.py', '__main__.py']
                for main_file in main_files:
                    main_path = self.root_path / main_file
                    if main_path.exists() and main_path not in all_deps:
                        all_deps.add(main_path)
            
            # Для конфигурационных файлов
            if 'config' in current_file.name.lower():
                # Ищем .env файлы
                for env_file in self.root_path.glob('**/.env*'):
                    if not self.should_skip(env_file):
                        all_deps.add(env_file)
        
        except Exception as e:
            print(f"⚠️  Ошибка при анализе специальных зависимостей {current_file}: {e}")
    
    def export_smart(self, target_file: str, output_file: Optional[str] = None):
        """
        Умный экспорт: целевой файл + все его зависимости
        
        Args:
            target_file: Путь к целевому файлу (например, 'app/ui/screens/catalog_screen.py')
            output_file: Имя выходного файла (если None - генерируется автоматически)
        """
        # Находим целевой файл
        target_path = self.root_path / target_file
        if not target_path.exists():
            # Пробуем найти файл
            found_files = list(self.root_path.glob(f"**/{target_file}"))
            if not found_files:
                raise FileNotFoundError(f"Файл {target_file} не найден в проекте")
            target_path = found_files[0]
            print(f"📁 Найден файл: {target_path.relative_to(self.root_path)}")
        
        # Находим все зависимости
        all_deps = self.find_dependencies(target_path)
        
        # Добавляем сам целевой файл
        files_to_export = {target_path}
        files_to_export.update(all_deps)
        
        # Добавляем основные файлы проекта
        main_files = [
            self.root_path / 'main.py',
            self.root_path / 'pyproject.toml',
            self.root_path / 'requirements.txt',
        ]
        
        for main_file in main_files:
            if main_file.exists():
                files_to_export.add(main_file)
        
        # Генерируем имя выходного файла
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_name = target_path.stem
            output_file = f"SMART_EXPORT_{target_name}_{timestamp}.md"
        
        # Экспортируем
        self._write_export(files_to_export, target_path, output_file)
        
        return output_file, len(files_to_export)
    
    def _write_export(self, files: Set[pathlib.Path], 
                     target_file: pathlib.Path,
                     output_file: str):
        """Записывает экспорт в файл"""
        
        # Сортируем файлы по пути
        sorted_files = sorted(files, key=lambda x: str(x.relative_to(self.root_path)))
        
        with open(output_file, 'w', encoding='utf-8') as out:
            # Заголовок
            target_rel = target_file.relative_to(self.root_path)
            out.write(f"# 🎯 Умный экспорт: {target_rel}\n")
            out.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"**Целевой файл:** `{target_rel}`\n")
            out.write(f"**Проект:** {self.root_path.name}\n\n")
            
            # Обзор зависимостей
            out.write("## 📊 Обзор зависимостей\n\n")
            
            # Граф зависимостей в текстовом виде
            out.write("```\n")
            out.write(f"Целевой файл: {target_rel}\n")
            out.write("Зависимости:\n")
            
            for file in sorted_files:
                if file == target_file:
                    continue
                rel_path = file.relative_to(self.root_path)
                out.write(f"  ├── {rel_path}\n")
            out.write("```\n\n")
            
            # Структура экспортируемых файлов
            out.write("## 📁 Структура экспорта\n\n")
            out.write("```\n")
            
            # Группируем по директориям
            dir_structure = {}
            for file in sorted_files:
                rel_path = file.relative_to(self.root_path)
                parent = str(rel_path.parent)
                if parent == '.':
                    parent = ''
                if parent not in dir_structure:
                    dir_structure[parent] = []
                dir_structure[parent].append(rel_path.name)
            
            # Выводим структуру
            def print_dir(dir_path: str, indent: int = 0):
                if dir_path in dir_structure:
                    prefix = "  " * indent
                    if dir_path:
                        out.write(f"{prefix}{dir_path.split('/')[-1]}/\n")
                    for file in sorted(dir_structure[dir_path]):
                        file_prefix = "  " * (indent + 1)
                        icon = "🎯" if dir_path == str(target_file.parent) and file == target_file.name else "📄"
                        out.write(f"{file_prefix}{icon} {file}\n")
                
                # Поддиректории
                subdirs = []
                if dir_path:
                    # Находим непосредственные поддиректории
                    dir_prefix = dir_path + '/'
                    subdirs = [
                        d for d in dir_structure.keys()
                        if d.startswith(dir_prefix) and dir_prefix.count('/') == d.count('/') - 1
                    ]
                else:
                    # Для корневой директории: все поддиректории первого уровня
                    subdirs = [
                        d for d in dir_structure.keys()
                        if d and '/' not in d
                    ]
                
                # Рекурсивно выводим поддиректории
                for subdir in sorted(set(subdirs)):
                    print_dir(subdir, indent + 1)
                    
            out.write("```\n\n")
            
            # Содержимое файлов
            out.write("## 📝 Содержимое файлов\n\n")
            
            total_size = 0
            file_count = 0
            
            for i, file in enumerate(sorted_files, 1):
                rel_path = file.relative_to(self.root_path)
                
                # Определяем язык для подсветки
                ext = file.suffix.lower()
                lang_map = {
                    '.py': 'python',
                    '.toml': 'toml',
                    '.txt': 'text',
                    '.ini': 'ini',
                    '.cfg': 'ini',
                    '.md': 'markdown',
                    '.json': 'json',
                    '.yml': 'yaml',
                    '.yaml': 'yaml',
                }
                lang = lang_map.get(ext, '')
                
                # Заголовок файла
                icon = "🎯" if file == target_file else "📄"
                out.write(f"### {icon} {rel_path}\n")
                
                if file == target_file:
                    out.write("**🔹 ЦЕЛЕВОЙ ФАЙЛ**  \n")
                
                # Информация о файле
                try:
                    file_size = file.stat().st_size
                    out.write(f"**Размер:** {file_size} байт  \n")
                    total_size += file_size
                    file_count += 1
                    
                    # Импорты для этого файла
                    if str(rel_path) in self.import_graph:
                        imports = self.import_graph[str(rel_path)]
                        if imports:
                            out.write(f"**Импортирует:** `{', '.join(sorted(imports))}`  \n")
                    
                except Exception as e:
                    out.write(f"**Ошибка:** {e}  \n")
                
                # Содержимое файла
                try:
                    # Читаем файл
                    try:
                        content = file.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            content = file.read_text(encoding='cp1251')
                        except:
                            content = f"# ⚠️ Файл в бинарном формате или неизвестной кодировке\n"
                    
                    # Обрезаем слишком большие файлы
                    max_lines = 500
                    lines = content.split('\n')
                    if len(lines) > max_lines:
                        content = '\n'.join(lines[:max_lines])
                        content += f"\n\n# ... файл обрезан, показано {max_lines} из {len(lines)} строк ..."
                    
                    out.write(f"```{lang}\n")
                    out.write(content)
                    if not content.endswith('\n'):
                        out.write('\n')
                    out.write("```\n\n")
                    
                except Exception as e:
                    out.write(f"```\n# ❌ Ошибка при чтении файла: {e}\n```\n\n")
            
            # Статистика
            out.write("## 📈 Статистика экспорта\n\n")
            out.write(f"- **Всего файлов:** {file_count}\n")
            out.write(f"- **Целевой файл:** `{target_rel}`\n")
            out.write(f"- **Зависимостей найдено:** {len(files) - 1}\n")
            out.write(f"- **Общий размер:** {total_size} байт ({total_size/1024:.1f} KB)\n")
            out.write(f"- **Глубина анализа:** {len(self.analyzed_files)} файлов проанализировано\n")
            
            # Рекомендации
            out.write("\n## 💡 Рекомендации по использованию\n\n")
            out.write("1. **Целевой файл** помечен значком 🎯\n")
            out.write("2. Порядок файлов соответствует структуре проекта\n")
            out.write("3. Зависимости включают:\n")
            out.write("   - Прямые импорты (import/from)\n")
            out.write("   - Родственные модули\n")
            out.write("   - Конфигурационные файлы\n")
            out.write("   - Основные файлы проекта (main.py и др.)\n")
            out.write("\n## 🔗 Граф зависимостей (текстовый)\n\n")
            out.write("```\n")
            self._write_dependency_graph(out, target_file)
            out.write("```\n")


    def _write_dependency_graph(self, out, target_file: pathlib.Path):
        """Записывает текстовый граф зависимостей"""
        target_rel = str(target_file.relative_to(self.root_path))
        
        # Собираем граф
        graph = {}
        for file, imports in self.import_graph.items():
            for imp in imports:
                # Находим файлы для этого импорта
                possible_files = []
                for dep_file in self.analyzed_files:
                    dep_rel = str(dep_file.relative_to(self.root_path))
                    if imp in dep_rel.replace('/', '.').replace('.py', ''):
                        possible_files.append(dep_rel)
                
                if possible_files:
                    if file not in graph:
                        graph[file] = []
                    graph[file].extend(possible_files)
        
        # Выводим граф
        out.write(f"{target_rel}\n")
        visited = set()
        
        def print_node(node: str, indent: int = 0):
            if node in visited:
                out.write("  " * indent + f"└── {node} (циклическая ссылка)\n")
                return
                
            visited.add(node)
            
            if node in graph:
                deps = graph[node]
                for i, dep in enumerate(sorted(deps)):
                    prefix = "  " * indent
                    if i == len(deps) - 1:
                        out.write(f"{prefix}└── {dep}\n")
                        print_node(dep, indent + 1)
                    else:
                        out.write(f"{prefix}├── {dep}\n")
                        print_node(dep, indent + 1)
        
        print_node(target_rel)


def find_pyproject_root() -> pathlib.Path:
    """Находит корень проекта по pyproject.toml"""
    current_dir = pathlib.Path.cwd()
    
    # Проверяем текущую директорию
    if (current_dir / "pyproject.toml").exists():
        return current_dir
    
    # Проверяем родительскую
    elif (current_dir.parent / "pyproject.toml").exists():
        print(f"📁 Pyproject.toml найден в родительской папке: {current_dir.parent}")
        choice = input("   Использовать родительскую папку как корень проекта? (y/n): ")
        if choice.lower() == 'y':
            return current_dir.parent
    
    return current_dir


def main():
    """Точка входа"""
    parser = argparse.ArgumentParser(
        description='Умный экспорт Python файла с зависимостями',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s catalog_screen.py          # Экспорт catalog_screen.py с зависимостями
  %(prog)s app/ui/screens/main_screen.py --output custom_export.md
  %(prog)s database.py --full         # Полный экспорт со всеми связями
        """
    )
    
    parser.add_argument(
        'target',
        help='Целевой файл для экспорта (например: catalog_screen.py или app/ui/screens/catalog_screen.py)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Имя выходного файла (если не указано - будет сгенерировано автоматически)'
    )
    
    parser.add_argument(
        '--root', '-r',
        help='Корневая директория проекта (по умолчанию - ищется pyproject.toml)'
    )
    
    parser.add_argument(
        '--full', '-f',
        action='store_true',
        help='Полный анализ зависимостей (может быть медленнее для больших проектов)'
    )
    
    args = parser.parse_args()
    
    print("🔍 Умный экспорт файла с зависимостями")
    print("=" * 50)
    
    # Определяем корень проекта
    if args.root:
        project_root = pathlib.Path(args.root).resolve()
        if not project_root.exists():
            print(f"❌ Директория не найдена: {args.root}")
            return
    else:
        project_root = find_pyproject_root()
    
    print(f"📂 Корень проекта: {project_root}")
    print(f"🎯 Целевой файл: {args.target}")
    
    # Создаем экспортер
    exporter = SmartProjectExporter(project_root)
    
    try:
        # Выполняем экспорт
        output_file, file_count = exporter.export_smart(args.target, args.output)
        
        print(f"✅ Экспорт успешно завершен!")
        print(f"📄 Выходной файл: {output_file}")
        print(f"📊 Файлов экспортировано: {file_count}")
        print(f"🔗 Зависимостей найдено: {file_count - 1}")
        print("\n📋 Что содержит экспорт:")
        print("   1. Целевой файл (помечен 🎯)")
        print("   2. Все его зависимости (import/from)")
        print("   3. Конфигурационные файлы")
        print("   4. Основные файлы проекта")
        print("   5. Граф зависимостей в текстовом виде")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\n💡 Попробуйте:")
        print(f"   1. Указать полный путь: app/ui/screens/catalog_screen.py")
        print(f"   2. Убедиться, что файл существует в проекте")
        print(f"   3. Проверить текущую директорию: {project_root}")
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()