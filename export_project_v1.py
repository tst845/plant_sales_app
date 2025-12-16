import os
import pathlib
from datetime import datetime

def export_project(root_path=".", output_file="project_export.md"):
    """
    Экспортирует структуру и код проекта в один Markdown файл.
    """
    
    # Директории для исключения
    exclude_dirs = {
        '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
        'venv', '.venv', 'env', '.env', 'envs',
        '.vscode', '.idea', 'vs_code',
        'dist', 'build', '*.egg-info',
        'node_modules', 'coverage', '.coverage',
        '.github', '.gitlab', '.bitbucket',
        'poetry_env', 'virtual_env'  # добавил специфичные для poetry
    }
    
    # Файлы для исключения
    exclude_files = {
        '*.pyc', '*.pyo', '*.pyd', '*.so',
        '*.db', '*.sqlite', '*.sqlite3', '*.log',
        'poetry.lock', 'package-lock.json', 'yarn.lock',
        '.gitignore', '.env', '.env.local', '.env.*',
        'Thumbs.db', 'desktop.ini'
    }
    
    root_path = pathlib.Path(root_path).resolve()
    
    with open(output_file, 'w', encoding='utf-8') as out:
        # Заголовок
        out.write(f"# Экспорт проекта: {root_path.name}\n")
        out.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"**Путь:** {root_path}\n\n")
        
        # Структура проекта
        out.write("## Структура проекта\n\n")
        out.write("```\n")
        
        # Сначала собираем структуру
        structure_lines = []
        
        for root, dirs, files in os.walk(root_path):
            # Фильтруем директории
            dirs[:] = [
                d for d in dirs 
                if d not in exclude_dirs 
                and not d.startswith('.')
                and not d.endswith('__pycache__')
            ]
            
            # Относительный путь
            try:
                rel_root = pathlib.Path(root).relative_to(root_path)
            except ValueError:
                continue
            
            # Определяем отступ
            if str(rel_root) == '.':
                indent_level = 0
            else:
                indent_level = len(rel_root.parts)
            
            indent = "  " * indent_level
            
            if str(rel_root) != '.':
                structure_lines.append(f"{indent}{rel_root.name}/")
            
            # Файлы
            for file in sorted(files):
                if any(file.endswith(ext.strip('*')) for ext in exclude_files if '*' in ext):
                    continue
                if file in exclude_files:
                    continue
                if any(file == pattern for pattern in exclude_files):
                    continue
                    
                structure_lines.append(f"{indent}  {file}")
        
        # Записываем структуру
        for line in structure_lines:
            out.write(f"{line}\n")
        
        out.write("```\n\n")
        
        # Содержимое файлов
        out.write("## Содержимое файлов\n\n")
        
        file_count = 0
        total_size = 0
        excluded_count = 0
        
        for root, dirs, files in os.walk(root_path):
            # Фильтруем директории
            dirs[:] = [
                d for d in dirs 
                if d not in exclude_dirs 
                and not d.startswith('.')
                and not d.endswith('__pycache__')
            ]
            
            for file in sorted(files):
                file_path = pathlib.Path(root) / file
                
                # Проверяем исключения для файлов
                skip = False
                
                # Проверка по расширению (шаблоны типа *.pyc)
                for pattern in exclude_files:
                    if pattern.startswith('*'):
                        ext = pattern[1:]  # убираем звездочку
                        if file.endswith(ext):
                            excluded_count += 1
                            skip = True
                            break
                    elif file == pattern:
                        excluded_count += 1
                        skip = True
                        break
                
                if skip:
                    continue
                
                # Дополнительные проверки
                if file.startswith('.'):
                    excluded_count += 1
                    continue
                
                try:
                    rel_path = file_path.relative_to(root_path)
                except ValueError:
                    continue
                
                # Определяем язык для подсветки синтаксиса
                ext = file_path.suffix.lower()
                lang_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript',
                    '.html': 'html',
                    '.css': 'css',
                    '.md': 'markdown',
                    '.json': 'json',
                    '.yml': 'yaml',
                    '.yaml': 'yaml',
                    '.txt': 'text',
                    '.toml': 'toml',
                    '.ini': 'ini',
                    '.xml': 'xml',
                    '.csv': 'csv',
                    '.sql': 'sql',
                }
                lang = lang_map.get(ext, '')
                
                out.write(f"### 📄 {rel_path}\n")
                out.write(f"**Размер:** {file_path.stat().st_size} байт  \n")
                
                try:
                    # Читаем файл с обработкой разных кодировок
                    try:
                        content = file_path.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            content = file_path.read_text(encoding='cp1251')
                        except:
                            content = f"# Не удалось прочитать файл (бинарный или неизвестная кодировка)\n"
                    
                    # Обрезаем слишком большие файлы
                    max_lines = 1000
                    lines = content.split('\n')
                    if len(lines) > max_lines:
                        content = '\n'.join(lines[:max_lines])
                        content += f"\n\n# ... файл обрезан, показано {max_lines} из {len(lines)} строк ..."
                    
                    out.write(f"```{lang}\n")
                    out.write(content)
                    if not content.endswith('\n'):
                        out.write('\n')
                    out.write("```\n\n")
                    
                    file_count += 1
                    total_size += file_path.stat().st_size
                    
                except Exception as e:
                    out.write(f"```\n# Ошибка при чтении файла: {e}\n```\n\n")
        
        # Статистика
        out.write("## Статистика\n\n")
        out.write(f"- **Экспортировано файлов:** {file_count}\n")
        out.write(f"- **Исключено файлов:** {excluded_count}\n")
        out.write(f"- **Общий размер:** {total_size} байт ({total_size/1024:.2f} KB)\n")
        out.write(f"- **Дата экспорта:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    print("🔍 Поиск корня Poetry проекта...")
    current_dir = pathlib.Path.cwd()
    
    # Ищем pyproject.toml в текущей или родительской директории
    project_root = None
    
    # Проверяем текущую директорию
    if (current_dir / "pyproject.toml").exists():
        project_root = current_dir
        print(f"✅ Найден Poetry проект в текущей папке: {project_root}")
    
    # Если не нашли, проверяем родительскую
    elif (current_dir.parent / "pyproject.toml").exists():
        project_root = current_dir.parent
        print(f"⚠️  Pyproject.toml найден в родительской папке: {project_root}")
        print(f"   Текущая папка: {current_dir.name}")
        choice = input("   Экспортировать из родительской папки? (y/n): ")
        if choice.lower() != 'y':
            project_root = current_dir
    
    # Если pyproject.toml не найден, используем текущую директорию
    if project_root is None:
        project_root = current_dir
        print(f"⚠️  Pyproject.toml не найден, экспортирую текущую папку: {project_root}")
    
    # Создаем имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"PROJECT_EXPORT_{timestamp}.md"
    
    print(f"📂 Экспорт из: {project_root}")
    print(f"📄 Выходной файл: {output_filename}")
    print("⏳ Выполняется экспорт...")
    
    try:
        export_project(project_root, output_filename)
        print(f"✅ Экспорт успешно завершен!")
        print(f"📊 Файл сохранен как: {output_filename}")
        print("\n📋 Что делать дальше:")
        print(f"   1. Откройте файл в VS Code: code {output_filename}")
        print(f"   2. Или просмотрите в любом Markdown-редакторе")
        print(f"   3. Файл содержит полную структуру и код проекта")
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
        print("🔄 Попробуйте запустить скрипт из корневой папки проекта:")
        print(f"   cd {project_root}")
        print("   python export_project_v2.py")