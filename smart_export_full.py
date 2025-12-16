import os
import ast
import pathlib
import argparse
from datetime import datetime
from typing import Set, List, Dict, Optional
import re
import sqlite3
import json

class SmartProjectExporter:
    """
    Умный экспорт проекта с зависимостями.
    Экспортирует структуру, целевой файл и все его зависимости.
    Включает полное содержимое файлов и структуру базы данных.
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
            'generated_docs'
        }
        
        # Файлы для исключения
        self.exclude_files = {
            '*.pyc', '*.pyo', '*.pyd', '*.so',
            '*.log',
            'poetry.lock', 'package-lock.json', 'yarn.lock',
            '.gitignore', '.env', '.env.local', '.env.*',
            'Thumbs.db', 'desktop.ini', '.DS_Store',
            'advanced_documentation.py'  # Исключаем файл генерации документации
        }
        
        # Полные пути для исключения (относительно корня проекта)
        self.exclude_full_paths = {
            'advanced_documentation.py',  # Файл в корне проекта
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
        
        # Проверяем полный путь файла относительно корня проекта
        try:
            rel_path = str(path.relative_to(self.root_path))
            if rel_path in self.exclude_full_paths:
                return True
        except ValueError:
            pass
        
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
                        imports.add(alias.name.split('.')[0])
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
                    elif node.level > 0:
                        current_dir = file_path.parent
                        for i in range(node.level - 1):
                            current_dir = current_dir.parent
                        for name_obj in node.names:
                            possible_names = [
                                f"{name_obj.name}.py",
                                f"{name_obj.name}/__init__.py"
                            ]
                            for possible in possible_names:
                                possible_path = current_dir / possible
                                if possible_path.exists():
                                    rel_path = possible_path.relative_to(self.root_path)
                                    imports.add(str(rel_path).replace('.py', '').replace('/', '.'))
            
            # Анализ строковых импортов
            string_imports = re.findall(r"from\s+['\"](.+?)['\"]", content)
            string_imports += re.findall(r"import\s+['\"](.+?)['\"]", content)
            
            for imp in string_imports:
                imports.add(imp.split('.')[0])
                
        except Exception as e:
            print(f"Ошибка анализа {file_path}: {e}")
        
        return imports
    
    def find_dependencies(self, target_file: pathlib.Path) -> Set[pathlib.Path]:
        """Находит все зависимости для целевого файла"""
        all_deps = set()
        to_analyze = {target_file}
        
        print(f"Поиск зависимостей для {target_file.name}...")
        
        while to_analyze:
            current_file = to_analyze.pop()
            
            if current_file in self.analyzed_files:
                continue
                
            self.analyzed_files.add(current_file)
            
            if not current_file.exists():
                print(f"Файл не найден: {current_file}")
                continue
            
            imports = self.analyze_imports(current_file)
            self.import_graph[str(current_file.relative_to(self.root_path))] = imports
            
            for imp in imports:
                found_files = self.find_file_by_import(imp, current_file.parent)
                for found_file in found_files:
                    if found_file not in self.analyzed_files:
                        to_analyze.add(found_file)
                        all_deps.add(found_file)
            
            self._add_special_dependencies(current_file, all_deps, to_analyze)
        
        return all_deps
    
    def find_file_by_import(self, import_name: str, search_from: pathlib.Path) -> List[pathlib.Path]:
        """Находит файл по имени импорта"""
        found_files = []
        
        possible_paths = [
            self.root_path / import_name.replace('.', '/') / '__init__.py',
            self.root_path / f"{import_name.replace('.', '/')}.py",
            search_from / f"{import_name}.py",
            search_from / import_name / '__init__.py',
            self.root_path / 'app' / import_name.replace('.', '/') / '__init__.py',
            self.root_path / 'app' / f"{import_name.replace('.', '/')}.py",
        ]
        
        for pattern in [f"**/{import_name}.py", f"**/{import_name}/__init__.py"]:
            try:
                for found in self.root_path.glob(pattern):
                    if not self.should_skip(found):
                        found_files.append(found)
            except Exception:
                pass
        
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
            
            if 'database' in current_file.name.lower() or 'db' in current_file.name.lower():
                for pattern in ['**/config.py', '**/configs.py', '**/settings.py', '**/models.py', '**/schema.py']:
                    for config_file in self.root_path.glob(pattern):
                        if not self.should_skip(config_file) and config_file not in all_deps:
                            all_deps.add(config_file)
                            to_analyze.add(config_file)
            
            if any(x in current_rel for x in ['screen', 'widget', 'ui']):
                for pattern in ['**/widgets/**/*.py', '**/ui/**/*.py']:
                    for ui_file in self.root_path.glob(pattern):
                        if not self.should_skip(ui_file) and ui_file != current_file:
                            try:
                                with open(ui_file, 'r', encoding='utf-8') as f_ui:
                                    ui_content = f_ui.read()
                                ui_name = ui_file.stem
                                if ui_name in content or ui_name in current_rel:
                                    all_deps.add(ui_file)
                            except:
                                pass
                
                main_files = ['main.py', 'app.py', '__main__.py']
                for main_file in main_files:
                    main_path = self.root_path / main_file
                    if main_path.exists() and main_path not in all_deps:
                        all_deps.add(main_path)
            
            if 'config' in current_file.name.lower():
                for env_file in self.root_path.glob('**/.env*'):
                    if not self.should_skip(env_file):
                        all_deps.add(env_file)
        
        except Exception as e:
            print(f"Ошибка при анализе специальных зависимостей {current_file}: {e}")
    
    def _get_database_structure(self) -> str:
        """Получает структуру базы данных (без данных)"""
        db_structure = "## Структура базы данных\n\n"
        
        db_extensions = ['.db', '.sqlite', '.sqlite3']
        db_files = []
        
        for ext in db_extensions:
            for db_file in self.root_path.glob(f"**/*{ext}"):
                if not self.should_skip(db_file):
                    db_files.append(db_file)
        
        if not db_files:
            db_structure += "Файлы базы данных не найдены.\n\n"
            return db_structure
        
        for db_file in db_files:
            db_structure += f"### База данных: `{db_file.relative_to(self.root_path)}`\n\n"
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
                tables = cursor.fetchall()
                
                if not tables:
                    db_structure += "Таблицы не найдены.\n\n"
                    continue
                
                db_structure += "**Таблицы:**\n\n"
                
                for table in tables:
                    table_name = table[0]
                    if table_name == 'sqlite_sequence':
                        continue
                    
                    db_structure += f"#### Таблица: `{table_name}`\n\n"
                    
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    
                    db_structure += "| Колонка | Тип | Nullable | Default | PK |\n"
                    db_structure += "|---------|-----|----------|---------|----|\n"
                    
                    for col in columns:
                        col_id, col_name, col_type, not_null, default_val, pk = col
                        nullable = "Нет" if not_null else "Да"
                        is_pk = "Да" if pk else "Нет"
                        default_val = default_val if default_val else "NULL"
                        db_structure += f"| `{col_name}` | `{col_type}` | {nullable} | `{default_val}` | {is_pk} |\n"
                    
                    db_structure += "\n"
                    
                    cursor.execute(f"PRAGMA index_list({table_name});")
                    indexes = cursor.fetchall()
                    
                    if indexes:
                        db_structure += "**Индексы:**\n\n"
                        for idx in indexes:
                            idx_id, idx_name, unique = idx
                            cursor.execute(f"PRAGMA index_info({idx_name});")
                            idx_cols = cursor.fetchall()
                            col_names = [col[2] for col in idx_cols]
                            unique_str = "Уникальный" if unique else "Неуникальный"
                            db_structure += f"- `{idx_name}` ({unique_str}): {', '.join(col_names)}\n"
                        db_structure += "\n"
                    
                    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                    fks = cursor.fetchall()
                    
                    if fks:
                        db_structure += "**Внешние ключи:**\n\n"
                        for fk in fks:
                            id_, seq, table_from, table_to, col_from, col_to, on_update, on_delete, match = fk
                            db_structure += f"- `{col_from}` → `{table_to}.{col_to}` "
                            db_structure += f"(ON UPDATE: {on_update}, ON DELETE: {on_delete})\n"
                        db_structure += "\n"
                
                conn.close()
                
            except Exception as e:
                db_structure += f"Ошибка при чтении базы данных: {e}\n\n"
        
        return db_structure
    
    def _find_database_related_files(self) -> Set[pathlib.Path]:
        """Находит файлы, связанные с работой с базой данных"""
        db_files = set()
        
        keywords = ['database', 'db', 'model', 'schema', 'table', 'migration']
        
        for pattern in ['**/*.py', '**/*.pyi']:
            for file_path in self.root_path.glob(pattern):
                if self.should_skip(file_path):
                    continue
                
                file_name_lower = file_path.name.lower()
                if any(keyword in file_name_lower for keyword in keywords):
                    db_files.add(file_path)
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    db_indicators = [
                        'sqlalchemy', 'create table', 'create database',
                        'foreign key', 'primary key', 'db.session',
                        'db.execute', 'cursor.execute', 'sqlite3',
                        'orm', 'declarative_base', 'db.Model'
                    ]
                    
                    if any(indicator in content for indicator in db_indicators):
                        db_files.add(file_path)
                        
                except:
                    pass
        
        return db_files
    
    def export_smart(self, target_file: str, output_file: Optional[str] = None):
        """
        Умный экспорт: целевой файл + все его зависимости + структура БД
        
        Args:
            target_file: Путь к целевому файлу
            output_file: Имя выходного файла
        """
        target_path = self.root_path / target_file
        if not target_path.exists():
            found_files = list(self.root_path.glob(f"**/{target_file}"))
            if not found_files:
                raise FileNotFoundError(f"Файл {target_file} не найден в проекте")
            target_path = found_files[0]
            print(f"Найден файл: {target_path.relative_to(self.root_path)}")
        
        all_deps = self.find_dependencies(target_path)
        
        files_to_export = {target_path}
        files_to_export.update(all_deps)
        
        db_related_files = self._find_database_related_files()
        files_to_export.update(db_related_files)
        
        main_files = [
            self.root_path / 'main.py',
            self.root_path / 'pyproject.toml',
            self.root_path / 'requirements.txt',
        ]
        
        for main_file in main_files:
            if main_file.exists():
                files_to_export.add(main_file)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_name = target_path.stem
            output_file = f"SMART_EXPORT_{target_name}_{timestamp}.md"
        
        self._write_export(files_to_export, target_path, output_file)
        
        return output_file, len(files_to_export)
    
    def _write_export(self, files: Set[pathlib.Path], 
                     target_file: pathlib.Path,
                     output_file: str):
        """Записывает экспорт в файл"""
        
        sorted_files = sorted(files, key=lambda x: str(x.relative_to(self.root_path)))
        
        with open(output_file, 'w', encoding='utf-8') as out:
            target_rel = target_file.relative_to(self.root_path)
            out.write(f"# Умный экспорт: {target_rel}\n")
            out.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"**Целевой файл:** `{target_rel}`\n")
            out.write(f"**Проект:** {self.root_path.name}\n\n")
            
            out.write("## Обзор зависимостей\n\n")
            
            out.write("```\n")
            out.write(f"Целевой файл: {target_rel}\n")
            out.write("Зависимости:\n")
            
            for file in sorted_files:
                if file == target_file:
                    continue
                rel_path = file.relative_to(self.root_path)
                out.write(f"  ├── {rel_path}\n")
            out.write("```\n\n")
            
            out.write("## Структура экспорта\n\n")
            out.write("```\n")
            
            dir_structure = {}
            for file in sorted_files:
                rel_path = file.relative_to(self.root_path)
                parent = str(rel_path.parent)
                if parent == '.':
                    parent = ''
                if parent not in dir_structure:
                    dir_structure[parent] = []
                dir_structure[parent].append(rel_path.name)
            
            def print_dir(dir_path: str, indent: int = 0):
                if dir_path in dir_structure:
                    prefix = "  " * indent
                    if dir_path:
                        out.write(f"{prefix}{dir_path.split('/')[-1]}/\n")
                    for file in sorted(dir_structure[dir_path]):
                        file_prefix = "  " * (indent + 1)
                        icon = ">>>" if dir_path == str(target_file.parent) and file == target_file.name else "   "
                        out.write(f"{file_prefix}{icon} {file}\n")
                
                subdirs = []
                if dir_path:
                    dir_prefix = dir_path + '/'
                    subdirs = [
                        d for d in dir_structure.keys()
                        if d.startswith(dir_prefix) and dir_prefix.count('/') == d.count('/') - 1
                    ]
                else:
                    subdirs = [
                        d for d in dir_structure.keys()
                        if d and '/' not in d
                    ]
                
                for subdir in sorted(set(subdirs)):
                    print_dir(subdir, indent + 1)
                    
            out.write("```\n\n")
            
            db_structure = self._get_database_structure()
            out.write(db_structure)
            
            out.write("## Содержимое файлов\n\n")
            
            total_size = 0
            file_count = 0
            
            for i, file in enumerate(sorted_files, 1):
                rel_path = file.relative_to(self.root_path)
                
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
                
                out.write(f"### {rel_path}\n")
                
                if file == target_file:
                    out.write("**ЦЕЛЕВОЙ ФАЙЛ**  \n")
                
                try:
                    file_size = file.stat().st_size
                    out.write(f"**Размер:** {file_size} байт  \n")
                    total_size += file_size
                    file_count += 1
                    
                    if str(rel_path) in self.import_graph:
                        imports = self.import_graph[str(rel_path)]
                        if imports:
                            out.write(f"**Импортирует:** `{', '.join(sorted(imports))}`  \n")
                    
                except Exception as e:
                    out.write(f"**Ошибка:** {e}  \n")
                
                try:
                    try:
                        content = file.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            content = file.read_text(encoding='cp1251')
                        except:
                            content = f"Файл в бинарном формате или неизвестной кодировке\n"
                    
                    out.write(f"```{lang}\n")
                    out.write(content)
                    if not content.endswith('\n'):
                        out.write('\n')
                    out.write("```\n\n")
                    
                except Exception as e:
                    out.write(f"```\nОшибка при чтении файла: {e}\n```\n\n")
            
            out.write("## Статистика экспорта\n\n")
            out.write(f"- **Всего файлов:** {file_count}\n")
            out.write(f"- **Целевой файл:** `{target_rel}`\n")
            out.write(f"- **Зависимостей найдено:** {len(files) - 1}\n")
            out.write(f"- **Общий размер:** {total_size} байт ({total_size/1024:.1f} KB)\n")
            out.write(f"- **Глубина анализа:** {len(self.analyzed_files)} файлов проанализировано\n")
            
            out.write("\n## Рекомендации по использованию\n\n")
            out.write("1. **Целевой файл** помечен значком >>>\n")
            out.write("2. Порядок файлов соответствует структуре проекта\n")
            out.write("3. **Исключены из экспорта:**\n")
            out.write("   - Файл advanced_documentation.py (генерация документации)\n")
            out.write("   - Служебные файлы и директории\n")
            out.write("4. Зависимости включают:\n")
            out.write("   - Прямые импорты (import/from)\n")
            out.write("   - Родственные модули\n")
            out.write("   - Конфигурационные файлы\n")
            out.write("   - Основные файлы проекта (main.py и др.)\n")
            out.write("5. **Структура базы данных** включает:\n")
            out.write("   - Все таблицы и их колонки\n")
            out.write("   - Индексы и внешние ключи\n")
            out.write("   - Файлы моделей и схем\n")
            out.write("\n## Граф зависимостей (текстовый)\n\n")
            out.write("```\n")
            self._write_dependency_graph(out, target_file)
            out.write("```\n")

    def _write_dependency_graph(self, out, target_file: pathlib.Path):
        """Записывает текстовый граф зависимостей"""
        target_rel = str(target_file.relative_to(self.root_path))
        
        graph = {}
        for file, imports in self.import_graph.items():
            for imp in imports:
                possible_files = []
                for dep_file in self.analyzed_files:
                    dep_rel = str(dep_file.relative_to(self.root_path))
                    if imp in dep_rel.replace('/', '.').replace('.py', ''):
                        possible_files.append(dep_rel)
                
                if possible_files:
                    if file not in graph:
                        graph[file] = []
                    graph[file].extend(possible_files)
        
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
    
    if (current_dir / "pyproject.toml").exists():
        return current_dir
    
    elif (current_dir.parent / "pyproject.toml").exists():
        print(f"Pyproject.toml найден в родительской папке: {current_dir.parent}")
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
    
    print("Умный экспорт файла с зависимостями")
    print("=" * 50)
    
    if args.root:
        project_root = pathlib.Path(args.root).resolve()
        if not project_root.exists():
            print(f"Директория не найдена: {args.root}")
            return
    else:
        project_root = find_pyproject_root()
    
    print(f"Корень проекта: {project_root}")
    print(f"Целевой файл: {args.target}")
    
    exporter = SmartProjectExporter(project_root)
    
    try:
        output_file, file_count = exporter.export_smart(args.target, args.output)
        
        print(f"Экспорт успешно завершен!")
        print(f"Выходной файл: {output_file}")
        print(f"Файлов экспортировано: {file_count}")
        print(f"Зависимостей найдено: {file_count - 1}")
        print("\nЧто содержит экспорт:")
        print("   1. Целевой файл (полное содержимое)")
        print("   2. Все его зависимости (import/from)")
        print("   3. Структуру базы данных (без данных)")
        print("   4. Файлы моделей и работы с БД")
        print("   5. Конфигурационные файлы")
        print("   6. Основные файлы проекта")
        print("   7. Граф зависимостей в текстовом виде")
        print("\nИсключено из экспорта:")
        print("   1. advanced_documentation.py (файл генерации документации)")
        
    except FileNotFoundError as e:
        print(f"{e}")
        print("\nПопробуйте:")
        print(f"   1. Указать полный путь: app/ui/screens/catalog_screen.py")
        print(f"   2. Убедиться, что файл существует в проекте")
        print(f"   3. Проверить текущую директорию: {project_root}")
        
    except Exception as e:
        print(f"Ошибка при экспорте: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()