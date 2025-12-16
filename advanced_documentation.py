#!/usr/bin/env python3
"""
Advanced Project Documentation Generator
Автоматически создает полную документацию проекта с анализом зависимостей,
type hints и диаграммами связей.
"""

import os
import ast
import json
import pathlib
import inspect
import argparse
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import yaml
import graphviz  # pip install graphviz

try:
    from graphviz import Digraph
except ImportError:
    Digraph = None
    print("⚠️  Для генерации диаграмм установите: pip install graphviz")


class ElementType(Enum):
    """Типы элементов кода"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    PROPERTY = "property"


@dataclass
class ArgumentInfo:
    """Информация об аргументе функции"""
    name: str
    type_hint: Optional[str] = None
    default: Optional[str] = None
    description: Optional[str] = None
    
    def __str__(self) -> str:
        result = self.name
        if self.type_hint:
            result += f": {self.type_hint}"
        if self.default:
            result += f" = {self.default}"
        return result


@dataclass
class FunctionInfo:
    """Информация о функции/методе"""
    name: str
    element_type: ElementType
    file_path: str
    line: int
    end_line: int
    docstring: Optional[str] = None
    args: List[ArgumentInfo] = field(default_factory=list)
    returns: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_static: bool = False
    is_classmethod: bool = False
    calls: List[str] = field(default_factory=list)  # Какие функции вызывает
    called_by: List[str] = field(default_factory=list)  # Кем вызывается
    raises: List[str] = field(default_factory=list)  # Какие исключения бросает
    
    @property
    def signature(self) -> str:
        """Генерирует строку сигнатуры"""
        async_prefix = "async " if self.is_async else ""
        args_str = ", ".join([str(arg) for arg in self.args])
        return_prefix = f" -> {self.returns}" if self.returns else ""
        decorators = ""
        if self.decorators:
            decorators = "\n".join([f"@{d}" for d in self.decorators]) + "\n"
        return f"{decorators}{async_prefix}def {self.name}({args_str}){return_prefix}"


@dataclass
class ClassInfo:
    """Информация о классе"""
    name: str
    file_path: str
    line: int
    end_line: int
    docstring: Optional[str] = None
    bases: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    methods: List[FunctionInfo] = field(default_factory=list)
    properties: List[FunctionInfo] = field(default_factory=list)
    class_vars: Dict[str, str] = field(default_factory=dict)  # {name: type_hint}
    inherits_from: List[str] = field(default_factory=list)  # Родительские классы
    used_by: List[str] = field(default_factory=list)  # Где используется
    inheritors: List[str] = field(default_factory=list)  # Кто наследует
    
    @property
    def inheritance_chain(self) -> str:
        """Цепочка наследования"""
        if not self.bases:
            return "object"
        return " → ".join(self.bases)


@dataclass
class ModuleInfo:
    """Информация о модуле"""
    name: str
    file_path: str
    relative_path: str
    docstring: Optional[str] = None
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)  # Что экспортирует (__all__)
    imported_by: List[str] = field(default_factory=list)  # Кто импортирует
    dependencies: List[str] = field(default_factory=list)  # От кого зависит
    

@dataclass
class ProjectStats:
    """Статистика проекта"""
    total_files: int = 0
    total_lines: int = 0
    total_classes: int = 0
    total_functions: int = 0
    total_methods: int = 0
    avg_complexity: float = 0.0
    docstring_coverage: float = 0.0
    type_hint_coverage: float = 0.0


class AdvancedDocumentationGenerator:
    """
    Продвинутый генератор документации для Python проектов.
    Анализирует AST, строит графы зависимостей и создает полную документацию.
    """
    
    def __init__(self, project_root: str = ".", config_file: Optional[str] = None):
        self.project_root = pathlib.Path(project_root).resolve()
        self.modules: Dict[str, ModuleInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.functions: Dict[str, FunctionInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.call_graph: Dict[str, Set[str]] = {}
        self.inheritance_graph: Dict[str, Set[str]] = {}
        self.project_stats = ProjectStats()
        
        # Конфигурация
        self.config = self._load_config(config_file)
        
        # Директории для исключения
        self.exclude_dirs = set(self.config.get('exclude_dirs', [
            '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
            'venv', '.venv', 'env', '.env', 'envs', '.tox',
            '.vscode', '.idea', '.vs', 'vs_code',
            'dist', 'build', '*.egg-info', 'node_modules',
            'coverage', '.coverage', 'htmlcov', '.pytest_cache',
            '.github', '.gitlab', '.bitbucket',
            'docs', 'documentation', 'generated_docs'  # исключаем саму документацию
        ]))
        
        self.exclude_files = set(self.config.get('exclude_files', [
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
            '*.db', '*.sqlite', '*.sqlite3',
            '*.log', '*.tmp', '*.temp',
            'poetry.lock', 'package-lock.json', 'yarn.lock',
            'requirements.txt', 'Pipfile.lock',
            '.env', '.env.local', '.env.*',
            'Thumbs.db', 'desktop.ini',
            '*.DS_Store'
        ]))
        
        print(f"🔍 Инициализация генератора документации")
        print(f"📁 Проект: {self.project_root.name}")
        print(f"📂 Путь: {self.project_root}")
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Загрузка конфигурации из YAML файла"""
        default_config = {
            'output': {
                'markdown': True,
                'json': True,
                'html': False,
                'diagrams': True,
                'diagram_format': 'png',
                'output_dir': 'generated_docs'
            },
            'analysis': {
                'include_private': False,
                'include_tests': False,
                'max_file_size': 1000000,
                'follow_imports': True
            },
            'templates': {
                'module_template': None,
                'class_template': None
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                default_config.update(user_config)
                print(f"✅ Загружена конфигурация из {config_file}")
            except Exception as e:
                print(f"⚠️  Ошибка загрузки конфигурации: {e}")
        
        return default_config
    
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
    
    def analyze_project(self):
        """Полный анализ проекта"""
        print("\n🔍 Начинаем анализ проекта...")
        
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            root_path = pathlib.Path(root)
            
            # Фильтрация директорий
            dirs[:] = [d for d in dirs if not self.should_skip(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                if self.should_skip(file_path):
                    continue
                
                if file.endswith('.py'):
                    python_files.append(file_path)
        
        print(f"📄 Найдено Python файлов: {len(python_files)}")
        
        # Анализ каждого файла
        for i, file_path in enumerate(python_files, 1):
            print(f"  [{i}/{len(python_files)}] Анализ: {file_path.relative_to(self.project_root)}")
            self._analyze_file(file_path)
        
        # Пост-обработка: анализ зависимостей
        print("\n🔗 Анализ зависимостей...")
        self._analyze_dependencies()
        self._analyze_calls()
        self._analyze_inheritance()
        
        # Сбор статистики
        self._collect_statistics()
        
        print(f"\n✅ Анализ завершен!")
        print(f"   📊 Модулей: {len(self.modules)}")
        print(f"   🏛️  Классов: {len(self.classes)}")
        print(f"   ⚙️  Функций: {len([f for f in self.functions.values() if f.element_type == ElementType.FUNCTION])}")
        print(f"   🔗 Методов: {len([f for f in self.functions.values() if f.element_type == ElementType.METHOD])}")
    
    def _analyze_file(self, file_path: pathlib.Path):
        """Анализ одного Python файла"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Пропускаем слишком большие файлы
            if len(content) > self.config['analysis']['max_file_size']:
                print(f"    ⚠️  Пропущен (слишком большой)")
                return
            
            tree = ast.parse(content)
            
            # Создаем информацию о модуле
            rel_path = file_path.relative_to(self.project_root)
            module_name = str(rel_path).replace('.py', '').replace('/', '.').replace('\\', '.')
            
            module_info = ModuleInfo(
                name=file_path.stem,
                file_path=str(file_path),
                relative_path=str(rel_path),
                docstring=ast.get_docstring(tree)
            )
            
            # Анализ импортов
            self._analyze_imports(tree, module_info)
            
            # Анализ классов и функций
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, file_path, module_name)
                    module_info.classes.append(class_info)
                    
                    # Сохраняем в общий реестр
                    full_class_name = f"{module_name}.{class_info.name}"
                    self.classes[full_class_name] = class_info
                    
                elif isinstance(node, ast.FunctionDef):
                    # Проверяем, не является ли функция методом класса
                    parent_class = self._get_parent_class(node, tree)
                    if parent_class:
                        # Это метод - обработаем позже при анализе класса
                        continue
                    
                    func_info = self._extract_function_info(
                        node, file_path, module_name, 
                        ElementType.FUNCTION
                    )
                    module_info.functions.append(func_info)
                    
                    # Сохраняем в общий реестр
                    full_func_name = f"{module_name}.{func_info.name}"
                    self.functions[full_func_name] = func_info
            
            # Сохраняем модуль
            self.modules[module_name] = module_info
            
        except SyntaxError as e:
            print(f"    ❌ Ошибка синтаксиса: {e}")
        except Exception as e:
            print(f"    ❌ Ошибка анализа: {e}")
    
    def _analyze_imports(self, tree: ast.AST, module_info: ModuleInfo):
        """Анализ импортов в модуле"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_info.imports.append(alias.name)
                    
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ''
                for alias in node.names:
                    import_name = f"{module_name}.{alias.name}" if module_name else alias.name
                    module_info.imports.append(import_name)
    
    def _extract_class_info(self, node: ast.ClassDef, file_path: pathlib.Path, 
                           module_name: str) -> ClassInfo:
        """Извлечение информации о классе"""
        # Определяем конец класса
        end_line = node.lineno
        if node.body:
            end_line = node.body[-1].lineno if hasattr(node.body[-1], 'lineno') else node.lineno
        
        class_info = ClassInfo(
            name=node.name,
            file_path=str(file_path),
            line=node.lineno,
            end_line=end_line,
            docstring=ast.get_docstring(node),
            bases=[ast.unparse(base) for base in node.bases],
            decorators=[ast.unparse(decorator) for decorator in node.decorator_list]
        )
        
        # Анализ содержимого класса
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Определяем тип метода
                element_type = ElementType.METHOD
                is_static = False
                is_classmethod = False
                
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == 'staticmethod':
                            is_static = True
                        elif decorator.id == 'classmethod':
                            is_classmethod = True
                
                method_info = self._extract_function_info(
                    item, file_path, module_name,
                    element_type, is_static, is_classmethod
                )
                class_info.methods.append(method_info)
                
                # Сохраняем метод в общий реестр
                full_method_name = f"{module_name}.{class_info.name}.{method_info.name}"
                self.functions[full_method_name] = method_info
                
            elif isinstance(item, ast.AnnAssign):  # Аннотированные переменные
                if isinstance(item.target, ast.Name):
                    class_info.class_vars[item.target.id] = ast.unparse(item.annotation)
                    
            elif isinstance(item, ast.Assign):  # Обычные присваивания
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        # Пытаемся определить тип
                        type_hint = "Any"
                        if isinstance(item.value, ast.Constant):
                            type_hint = type(item.value.value).__name__
                        elif isinstance(item.value, ast.List):
                            type_hint = "List"
                        elif isinstance(item.value, ast.Dict):
                            type_hint = "Dict"
                        
                        class_info.class_vars[target.id] = type_hint
        
        return class_info
    
    def _extract_function_info(self, node: ast.FunctionDef, file_path: pathlib.Path,
                              module_name: str, element_type: ElementType,
                              is_static: bool = False, is_classmethod: bool = False) -> FunctionInfo:
        """Извлечение информации о функции/методе"""
        # Определяем конец функции
        end_line = node.lineno
        if node.body:
            last_node = node.body[-1]
            if hasattr(last_node, 'lineno'):
                end_line = last_node.lineno
        
        func_info = FunctionInfo(
            name=node.name,
            element_type=element_type,
            file_path=str(file_path),
            line=node.lineno,
            end_line=end_line,
            docstring=ast.get_docstring(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_static=is_static,
            is_classmethod=is_classmethod
        )
        
        # Анализ аргументов
        self._analyze_arguments(node, func_info)
        
        # Анализ декораторов
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in ['staticmethod', 'classmethod']:
                continue  # Уже обработали
            func_info.decorators.append(ast.unparse(decorator))
        
        # Анализ возвращаемого значения
        if node.returns:
            func_info.returns = ast.unparse(node.returns)
        
        # Анализ вызовов внутри функции
        calls = set()
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                if isinstance(item.func, ast.Name):
                    calls.add(item.func.id)
                elif isinstance(item.func, ast.Attribute):
                    calls.add(self._get_attribute_name(item.func))
        
        func_info.calls = list(calls)
        
        # Анализ исключений
        for item in ast.walk(node):
            if isinstance(item, ast.Raise):
                if isinstance(item.exc, ast.Call):
                    if isinstance(item.exc.func, ast.Name):
                        func_info.raises.append(item.exc.func.id)
        
        return func_info
    
    def _analyze_arguments(self, node: ast.FunctionDef, func_info: FunctionInfo):
        """Анализ аргументов функции"""
        # Позиционные аргументы
        for arg in node.args.args:
            arg_info = ArgumentInfo(name=arg.arg)
            if arg.annotation:
                arg_info.type_hint = ast.unparse(arg.annotation)
            func_info.args.append(arg_info)
        
        # Аргументы только для ключевых слов
        for arg in node.args.kwonlyargs:
            arg_info = ArgumentInfo(name=arg.arg)
            if arg.annotation:
                arg_info.type_hint = ast.unparse(arg.annotation)
            func_info.args.append(arg_info)
        
        # *args
        if node.args.vararg:
            arg_info = ArgumentInfo(name=f"*{node.args.vararg.arg}")
            if node.args.vararg.annotation:
                arg_info.type_hint = ast.unparse(node.args.vararg.annotation)
            func_info.args.append(arg_info)
        
        # **kwargs
        if node.args.kwarg:
            arg_info = ArgumentInfo(name=f"**{node.args.kwarg.arg}")
            if node.args.kwarg.annotation:
                arg_info.type_hint = ast.unparse(node.args.kwarg.annotation)
            func_info.args.append(arg_info)
        
        # Значения по умолчанию
        defaults_start = len(node.args.args) - len(node.args.defaults)
        for i, default in enumerate(node.args.defaults):
            idx = defaults_start + i
            if idx < len(func_info.args):
                func_info.args[idx].default = ast.unparse(default)
    
    def _get_parent_class(self, node: ast.FunctionDef, tree: ast.AST) -> Optional[str]:
        """Определить, является ли функция методом класса"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for child in parent.body:
                    if child == node:
                        return parent.name
        return None
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Получение полного имени атрибута"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))
    
    def _analyze_dependencies(self):
        """Анализ зависимостей между модулями"""
        for module_name, module_info in self.modules.items():
            self.dependency_graph[module_name] = set()
            
            for imp in module_info.imports:
                # Проверяем, является ли импорт внутренним модулем
                for other_module in self.modules.keys():
                    # Простая проверка: если имя модуля начинается с импорта
                    if imp.startswith(other_module.split('.')[0]):
                        self.dependency_graph[module_name].add(other_module)
                        module_info.dependencies.append(other_module)
                        
                        # Обновляем imported_by у другого модуля
                        if other_module in self.modules:
                            self.modules[other_module].imported_by.append(module_name)
    
    def _analyze_calls(self):
        """Анализ вызовов между функциями"""
        # Проходим по всем функциям и обновляем called_by
        for caller_name, caller_func in self.functions.items():
            for call in caller_func.calls:
                # Ищем функцию, которую вызывают
                for callee_name, callee_func in self.functions.items():
                    if callee_func.name == call or callee_name.endswith(f".{call}"):
                        if caller_name not in self.call_graph:
                            self.call_graph[caller_name] = set()
                        self.call_graph[caller_name].add(callee_name)
                        callee_func.called_by.append(caller_name)
    
    def _analyze_inheritance(self):
        """Анализ наследования классов"""
        for class_name, class_info in self.classes.items():
            for base in class_info.bases:
                # Ищем родительский класс в проекте
                for other_class_name, other_class_info in self.classes.items():
                    if other_class_info.name == base or other_class_name.endswith(f".{base}"):
                        class_info.inherits_from.append(other_class_name)
                        other_class_info.inheritors.append(class_name)
                        
                        if class_name not in self.inheritance_graph:
                            self.inheritance_graph[class_name] = set()
                        self.inheritance_graph[class_name].add(other_class_name)
    
    def _collect_statistics(self):
        """Сбор статистики проекта"""
        total_elements = 0
        total_with_docstrings = 0
        total_with_type_hints = 0
        
        # Статистика по функциям
        for func_info in self.functions.values():
            total_elements += 1
            if func_info.docstring:
                total_with_docstrings += 1
            if func_info.returns or any(arg.type_hint for arg in func_info.args):
                total_with_type_hints += 1
        
        # Статистика по классам
        for class_info in self.classes.values():
            total_elements += 1
            if class_info.docstring:
                total_with_docstrings += 1
        
        self.project_stats = ProjectStats(
            total_files=len(self.modules),
            total_classes=len(self.classes),
            total_functions=len([f for f in self.functions.values() 
                               if f.element_type == ElementType.FUNCTION]),
            total_methods=len([f for f in self.functions.values() 
                             if f.element_type == ElementType.METHOD]),
            docstring_coverage=(total_with_docstrings / total_elements * 100 
                               if total_elements > 0 else 0),
            type_hint_coverage=(total_with_type_hints / total_elements * 100 
                               if total_elements > 0 else 0)
        )
    
    def generate_markdown(self, output_file: str = "PROJECT_DOCUMENTATION.md"):
        """Генерация Markdown документации"""
        print(f"\n📝 Генерация Markdown документации...")
        
        output_dir = self.config['output']['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            self._write_markdown_header(f)
            self._write_markdown_toc(f)
            self._write_markdown_overview(f)
            self._write_markdown_modules(f)
            self._write_markdown_classes(f)
            self._write_markdown_functions(f)
            self._write_markdown_dependencies(f)
            self._write_markdown_statistics(f)
        
        print(f"✅ Markdown сохранен: {output_path}")
        return output_path
    
    def _write_markdown_header(self, f):
        """Запись заголовка документации"""
        f.write(f"""# 📚 Документация проекта: {self.project_root.name}

**Дата генерации:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Путь к проекту:** `{self.project_root}`  
**Версия документации:** 1.0.0  

> Автоматически сгенерировано с помощью AdvancedDocumentationGenerator

---

""")
    
    def _write_markdown_toc(self, f):
        """Запись оглавления"""
        f.write("## 📑 Оглавление\n\n")
        
        toc_items = [
            ("📊 Обзор проекта", "обзор-проекта"),
            ("📁 Модули", "модули"),
            ("🏛️ Классы", "классы"),
            ("⚙️ Функции", "функции"),
            ("🔗 Зависимости", "зависимости"),
            ("📈 Статистика", "статистика")
        ]
        
        for title, anchor in toc_items:
            f.write(f"- [{title}](#{anchor})\n")
        
        f.write("\n---\n\n")
    
    def _write_markdown_overview(self, f):
        """Запись обзора проекта"""
        f.write('<a id="обзор-проекта"></a>\n')
        f.write("## 📊 Обзор проекта\n\n")
        
        f.write(f"### Структура проекта\n")
        f.write("```\n")
        
        # Простая визуализация структуры
        modules_by_dir = {}
        for module_name in self.modules.keys():
            dir_path = os.path.dirname(module_name.replace('.', '/'))
            if dir_path not in modules_by_dir:
                modules_by_dir[dir_path] = []
            modules_by_dir[dir_path].append(module_name)
        
        def print_dir_structure(base_dir: str, indent: int = 0):
            if base_dir in modules_by_dir:
                for module in sorted(modules_by_dir[base_dir]):
                    module_name = module.split('.')[-1]
                    prefix = "    " * indent + "└── " if indent > 0 else ""
                    f.write(f"{prefix}📄 {module_name}.py\n")
            
            # Поддиректории
            subdirs = {d for d in modules_by_dir.keys() 
                      if d.startswith(base_dir + '/') and d != base_dir}
            for subdir in sorted(subdirs):
                dir_name = subdir.split('/')[-1]
                prefix = "    " * indent + "├── " if indent > 0 else ""
                f.write(f"{prefix}📁 {dir_name}/\n")
                print_dir_structure(subdir, indent + 1)
        
        print_dir_structure("")
        f.write("```\n\n")
        
        f.write("### Быстрый старт\n")
        f.write("```bash\n")
        f.write("# Установка зависимостей\n")
        f.write("pip install -r requirements.txt\n\n")
        f.write("# Запуск проекта\n")
        f.write("python main.py\n")
        f.write("```\n\n")
    
    def _write_markdown_modules(self, f):
        """Запись информации о модулях"""
        f.write('<a id="модули"></a>\n')
        f.write("## 📁 Модули\n\n")
        
        for module_name, module_info in sorted(self.modules.items()):
            f.write(f"### 🗂️ `{module_name}`\n")
            f.write(f"**Файл:** `{module_info.relative_path}`  \n")
            
            if module_info.docstring:
                f.write(f"\n**Описание:** {module_info.docstring}\n")
            
            # Импорты
            if module_info.imports:
                f.write(f"\n**Импортирует:**\n")
                for imp in sorted(module_info.imports)[:10]:  # Показываем первые 10
                    f.write(f"- `{imp}`\n")
                if len(module_info.imports) > 10:
                    f.write(f"- ... и еще {len(module_info.imports) - 10}\n")
            
            # Экспорты
            if module_info.exports:
                f.write(f"\n**Экспортирует:**\n")
                for exp in sorted(module_info.exports):
                    f.write(f"- `{exp}`\n")
            
            # Классы в модуле
            if module_info.classes:
                f.write(f"\n**Классы ({len(module_info.classes)}):**\n")
                for class_info in module_info.classes:
                    f.write(f"- `{class_info.name}` (строка {class_info.line})\n")
            
            # Функции в модуле
            if module_info.functions:
                f.write(f"\n**Функции ({len(module_info.functions)}):**\n")
                for func_info in module_info.functions:
                    async_prefix = "async " if func_info.is_async else ""
                    f.write(f"- `{async_prefix}{func_info.name}()` (строка {func_info.line})\n")
            
            f.write("\n---\n\n")
    
    def _write_markdown_classes(self, f):
        """Запись информации о классах"""
        if not self.classes:
            return
        
        f.write('<a id="классы"></a>\n')
        f.write("## 🏛️ Классы\n\n")
        
        for class_name, class_info in sorted(self.classes.items()):
            f.write(f"### 🏗️ `{class_info.name}`\n")
            f.write(f"**Расположение:** `{class_info.file_path}`  \n")
            f.write(f"**Строки:** {class_info.line}-{class_info.end_line}  \n")
            
            if class_info.docstring:
                f.write(f"\n**Описание:**\n\n{class_info.docstring}\n")
            
            # Наследование
            if class_info.bases:
                f.write(f"\n**Наследует от:** `{', '.join(class_info.bases)}`\n")
            
            if class_info.inherits_from:
                f.write(f"\n**Конкретные родители:**\n")
                for parent in class_info.inherits_from:
                    f.write(f"- `{parent}`\n")
            
            if class_info.inheritors:
                f.write(f"\n**Наследники:**\n")
                for inheritor in class_info.inheritors:
                    f.write(f"- `{inheritor}`\n")
            
            # Декораторы
            if class_info.decorators:
                f.write(f"\n**Декораторы:**\n")
                for decorator in class_info.decorators:
                    f.write(f"- `{decorator}`\n")
            
            # Переменные класса
            if class_info.class_vars:
                f.write(f"\n**Атрибуты класса:**\n")
                for var_name, var_type in sorted(class_info.class_vars.items()):
                    f.write(f"- `{var_name}: {var_type}`\n")
            
            # Методы
            if class_info.methods:
                f.write(f"\n**Методы ({len(class_info.methods)}):**\n\n")
                for method in class_info.methods:
                    self._write_function_details(f, method, indent="  ")
            
            f.write("\n---\n\n")
    
    def _write_markdown_functions(self, f):
        """Запись информации о функциях"""
        top_level_funcs = {k: v for k, v in self.functions.items() 
                          if v.element_type == ElementType.FUNCTION}
        
        if not top_level_funcs:
            return
        
        f.write('<a id="функции"></a>\n')
        f.write("## ⚙️ Функции\n\n")
        
        for func_name, func_info in sorted(top_level_funcs.items()):
            f.write(f"### 🔧 `{func_info.name}()`\n")
            f.write(f"**Расположение:** `{func_info.file_path}`  \n")
            f.write(f"**Строки:** {func_info.line}-{func_info.end_line}  \n")
            
            self._write_function_details(f, func_info)
            
            f.write("\n---\n\n")
    
    def _write_function_details(self, f, func_info: FunctionInfo, indent: str = ""):
        """Запись деталей функции"""
        f.write(f"{indent}```python\n")
        f.write(f"{indent}{func_info.signature}\n")
        f.write(f"{indent}```\n\n")
        
        if func_info.docstring:
            f.write(f"{indent}**Описание:**\n\n{indent}{func_info.docstring}\n\n")
        
        # Аргументы
        if func_info.args:
            f.write(f"{indent}**Аргументы:**\n")
            for arg in func_info.args:
                arg_desc = f"`{arg.name}`"
                if arg.type_hint:
                    arg_desc += f" → `{arg.type_hint}`"
                if arg.default:
                    arg_desc += f" (по умолчанию: `{arg.default}`)"
                f.write(f"{indent}- {arg_desc}\n")
            f.write("\n")
        
        # Возвращаемое значение
        if func_info.returns:
            f.write(f"{indent}**Возвращает:** `{func_info.returns}`\n\n")
        
        # Вызывает
        if func_info.calls:
            f.write(f"{indent}**Вызывает функции:**\n")
            for call in sorted(func_info.calls)[:5]:
                f.write(f"{indent}- `{call}`\n")
            if len(func_info.calls) > 5:
                f.write(f"{indent}- ... и еще {len(func_info.calls) - 5}\n")
            f.write("\n")
        
        # Вызывается
        if func_info.called_by:
            f.write(f"{indent}**Вызывается в:**\n")
            for caller in sorted(func_info.called_by)[:5]:
                f.write(f"{indent}- `{caller}`\n")
            if len(func_info.called_by) > 5:
                f.write(f"{indent}- ... и еще {len(func_info.called_by) - 5}\n")
            f.write("\n")
        
        # Исключения
        if func_info.raises:
            f.write(f"{indent}**Поднимает исключения:**\n")
            for exc in sorted(func_info.raises):
                f.write(f"{indent}- `{exc}`\n")
            f.write("\n")
        
        # Декораторы (кроме стандартных)
        non_standard_decorators = [d for d in func_info.decorators 
                                  if d not in ['staticmethod', 'classmethod', 'property']]
        if non_standard_decorators:
            f.write(f"{indent}**Декораторы:**\n")
            for decorator in non_standard_decorators:
                f.write(f"{indent}- `{decorator}`\n")
            f.write("\n")
    
    def _write_markdown_dependencies(self, f):
        """Запись информации о зависимостях"""
        f.write('<a id="зависимости"></a>\n')
        f.write("## 🔗 Зависимости\n\n")
        
        f.write("### Граф зависимостей модулей\n")

         # Альтернатива: текстовое представление
        f.write("```\n")
        for module, deps in sorted(self.dependency_graph.items()):
            if deps:
                short_name = module.split('.')[-1]
                f.write(f"{short_name}:\n")
                for dep in sorted(deps):
                    dep_short = dep.split('.')[-1]
                    f.write(f"  ← {dep_short}\n")
        f.write("```\n\n")
        
        # Mermaid диаграмма (работает в GitHub/GitLab Markdown)

        f.write("```mermaid\ngraph TD\n")
        
        # Упрощенный граф для Mermaid.js
        displayed_edges = set()
        for module, deps in self.dependency_graph.items():
            if deps:
                for dep in deps:
                    edge = (dep, module)
                    if edge not in displayed_edges:
                        # Короткие имена для отображения
                        from_name = dep.split('.')[-1]
                        to_name = module.split('.')[-1]
                        f.write(f"    {from_name} --> {to_name}\n")
                        displayed_edges.add(edge)
        
        f.write("```\n\n")
        
        f.write("### Внешние зависимости\n")
        external_deps = set()
        for module_info in self.modules.values():
            for imp in module_info.imports:
                # Простая эвристика для определения внешних зависимостей
                if not any(imp.startswith(m.split('.')[0]) for m in self.modules.keys()):
                    external_deps.add(imp.split('.')[0])
        
        if external_deps:
            for dep in sorted(external_deps):
                f.write(f"- `{dep}`\n")
        else:
            f.write("*Нет внешних зависимостей*\n")
        
        f.write("\n")
    
    def _write_markdown_statistics(self, f):
        """Запись статистики"""
        f.write('<a id="статистика"></a>\n')
        f.write("## 📈 Статистика проекта\n\n")
        
        stats = self.project_stats
        f.write("| Метрика | Значение |\n")
        f.write("|---------|----------|\n")
        f.write(f"| 📁 Файлов Python | {stats.total_files} |\n")
        f.write(f"| 🏛️ Классов | {stats.total_classes} |\n")
        f.write(f"| ⚙️ Функций | {stats.total_functions} |\n")
        f.write(f"| 🔗 Методов | {stats.total_methods} |\n")
        f.write(f"| 📝 Покрытие docstrings | {stats.docstring_coverage:.1f}% |\n")
        f.write(f"| 🎯 Покрытие type hints | {stats.type_hint_coverage:.1f}% |\n")
        
        f.write("\n### Рекомендации\n")
        
        if stats.docstring_coverage < 80:
            f.write("⚠️ **Низкое покрытие docstrings** - рекомендуется добавить документацию к функциям и классам.\n\n")
        
        if stats.type_hint_coverage < 50:
            f.write("⚠️ **Низкое покрытие type hints** - рекомендуется добавить аннотации типов для улучшения читаемости кода.\n\n")
        
        if not self.classes:
            f.write("ℹ️ **Нет классов** - проект использует функциональный стиль программирования.\n\n")
        else:
            avg_methods = sum(len(c.methods) for c in self.classes.values()) / len(self.classes)
            if avg_methods > 10:
                f.write("⚠️ **Среднее количество методов в классе высокое** - рассмотрите возможность рефакторинга (Принцип единой ответственности).\n\n")
    
    def generate_json(self, output_file: str = "documentation.json"):
        """Генерация JSON документации"""
        print(f"\n📊 Генерация JSON документации...")
        
        output_dir = self.config['output']['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, output_file)
        
        data = {
            "project": {
                "name": self.project_root.name,
                "path": str(self.project_root),
                "generated_at": datetime.now().isoformat(),
                "statistics": asdict(self.project_stats)
            },
            "modules": {k: asdict(v) for k, v in self.modules.items()},
            "classes": {k: asdict(v) for k, v in self.classes.items()},
            "functions": {k: asdict(v) for k, v in self.functions.items()},
            "graphs": {
                "dependencies": {k: list(v) for k, v in self.dependency_graph.items()},
                "calls": {k: list(v) for k, v in self.call_graph.items()},
                "inheritance": {k: list(v) for k, v in self.inheritance_graph.items()}
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ JSON сохранен: {output_path}")
        return output_path
    
    def generate_diagrams(self):
        """Генерация диаграмм зависимостей"""
        if not Digraph:
            print("⚠️  Python-пакет graphviz не установлен. Пропускаем генерацию диаграмм.")
            print("   Установите: pip install graphviz")
            return
        
        # Проверка наличия Graphviz в PATH
        try:
            import subprocess
            result = subprocess.run(['dot', '-V'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Graphviz не найден в PATH")
        except (FileNotFoundError, Exception) as e:
            print("\n⚠️  Graphviz executables не найдены в системе.")
            print("   Для генерации диаграмм необходимо установить Graphviz:")
            print("   1. Скачайте с https://graphviz.org/download/")
            print("   2. Установите, отметив 'Add to PATH'")
            print("   3. Перезапустите терминал/IDE")
            print("   4. Проверьте: dot -V")
            print("\n   Пропускаем генерацию диаграмм...")
            return
                
        print(f"\n📊 Генерация диаграмм...")
        
        output_dir = os.path.join(self.config['output']['output_dir'], "diagrams")
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Диаграмма зависимостей модулей
        self._generate_module_dependency_diagram(output_dir)
        
        # 2. Диаграмма наследования классов
        self._generate_inheritance_diagram(output_dir)
        
        # 3. Диаграмма вызовов функций
        self._generate_call_graph_diagram(output_dir)
        
        print(f"✅ Диаграммы сохранены в: {output_dir}")
    
    def _generate_module_dependency_diagram(self, output_dir: str):
        """Генерация диаграммы зависимостей модулей"""
        dot = Digraph(comment='Module Dependencies', format='png')
        dot.attr(rankdir='LR', size='8,5')
        dot.attr('node', shape='box', style='filled', color='lightblue')
        
        # Добавляем узлы
        for module_name in self.modules.keys():
            short_name = module_name.split('.')[-1]
            dot.node(module_name, short_name)
        
        # Добавляем ребра
        for module, deps in self.dependency_graph.items():
            for dep in deps:
                dot.edge(dep, module)
        
        output_path = os.path.join(output_dir, 'module_dependencies')
        dot.render(output_path, cleanup=True)
    
    def _generate_inheritance_diagram(self, output_dir: str):
        """Генерация диаграммы наследования классов"""
        if not self.inheritance_graph:
            return
        
        dot = Digraph(comment='Class Inheritance', format='png')
        dot.attr(rankdir='BT', size='8,5')  # Bottom to Top для наследования
        dot.attr('node', shape='box', style='filled', color='lightgreen')
        
        # Добавляем узлы
        for class_name in self.classes.keys():
            short_name = class_name.split('.')[-1]
            dot.node(class_name, short_name)
        
        # Добавляем ребра наследования
        for child, parents in self.inheritance_graph.items():
            for parent in parents:
                dot.edge(child, parent, style='dashed')
        
        output_path = os.path.join(output_dir, 'class_inheritance')
        dot.render(output_path, cleanup=True)
    
    def _generate_call_graph_diagram(self, output_dir: str):
        """Генерация диаграммы вызовов функций"""
        if not self.call_graph:
            return
        
        dot = Digraph(comment='Function Call Graph', format='png')
        dot.attr(rankdir='LR', size='8,5')
        dot.attr('node', shape='ellipse', style='filled', color='lightcoral')
        
        # Ограничиваем количество узлов для читаемости
        all_functions = list(self.call_graph.keys())
        if len(all_functions) > 50:
            print("   ⚠️  Слишком много функций для диаграммы. Ограничиваем 50 узлами.")
            all_functions = all_functions[:50]
        
        # Добавляем узлы
        for func_name in all_functions:
            short_name = func_name.split('.')[-1]
            dot.node(func_name, short_name)
        
        # Добавляем ребра вызовов
        for caller, callees in self.call_graph.items():
            if caller in all_functions:
                for callee in callees:
                    if callee in all_functions:
                        dot.edge(caller, callee)
        
        output_path = os.path.join(output_dir, 'function_calls')
        dot.render(output_path, cleanup=True)
    
    def generate_all(self):
        """Генерация всей документации"""
        print("\n" + "="*60)
        print("🚀 Запуск полной генерации документации")
        print("="*60)
        
        self.analyze_project()
        
        if self.config['output']['markdown']:
            self.generate_markdown()
        
        if self.config['output']['json']:
            self.generate_json()
        
        if self.config['output']['diagrams'] and Digraph:
            self.generate_diagrams()
        
        print("\n" + "="*60)
        print("🎉 Генерация документации завершена!")
        print("="*60)


def main():
    """Точка входа для запуска из командной строки"""
    parser = argparse.ArgumentParser(
        description='Advanced Python Project Documentation Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s .                      # Анализ текущей директории
  %(prog)s /path/to/project       # Анализ указанного пути
  %(prog)s . --json-only          # Только JSON
  %(prog)s . --no-diagrams        # Без диаграмм
  %(prog)s . --config config.yaml # С конфигурационным файлом
        """
    )
    
    parser.add_argument(
        'path', 
        nargs='?', 
        default='.',
        help='Путь к проекту (по умолчанию: текущая директория)'
    )
    
    parser.add_argument(
        '--config', 
        '-c',
        help='Путь к конфигурационному файлу YAML'
    )
    
    parser.add_argument(
        '--markdown-only',
        action='store_true',
        help='Генерировать только Markdown документацию'
    )
    
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Генерировать только JSON документацию'
    )
    
    parser.add_argument(
        '--no-diagrams',
        action='store_true',
        help='Не генерировать диаграммы'
    )
    
    parser.add_argument(
        '--output-dir',
        '-o',
        default='generated_docs',
        help='Директория для выходных файлов (по умолчанию: generated_docs)'
    )
    
    args = parser.parse_args()
    
    # Создаем конфигурацию на основе аргументов
    config = {
        'output': {
            'markdown': not args.json_only,
            'json': not args.markdown_only,
            'diagrams': not args.no_diagrams,
            'output_dir': args.output_dir
        }
    }
    
    # Запускаем генератор
    try:
        generator = AdvancedDocumentationGenerator(args.path, args.config)
        
        # Обновляем конфигурацию аргументами командной строки
        if args.markdown_only or args.json_only or args.no_diagrams:
            generator.config.update(config)
        
        generator.generate_all()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Генерация прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        if "Graphviz" in str(e) or "dot" in str(e):
            print("\n💡 Решение:")
            print("1. Установите Graphviz с https://graphviz.org/download/")
            print("2. При установке отметьте 'Add Graphviz to the system PATH'")
            print("3. Перезапустите терминал и проверьте: dot -V")
            print("4. Или запустите с флагом --no-diagrams")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()