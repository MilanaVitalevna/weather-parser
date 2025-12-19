import os
import platform
import shutil
import sys

import PyInstaller.__main__


def clean_build_dirs():
    """Очищает директории сборки от предыдущих артефактов."""
    dirs_to_clean = ["dist", "build"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Удаляем директорию: {dir_name}")
            shutil.rmtree(dir_name)


def get_data_format(src, dst):
    """Возвращает строку для --add-data в правильном формате для текущей ОС."""
    if platform.system() == "Windows":
        return f"{src};{dst}"
    else:
        return f"{src}:{dst}"


def main():
    print("Начинаем сборку Weather Parser...")
    print(f"Операционная система: {platform.system()}")
    clean_build_dirs()

    # Базовые аргументы PyInstaller
    pyinstaller_args = [
        "src/main.py",  # Точка входа
        "--onefile",  # Один исполняемый файл
        "--windowed",  # Не показывать консоль (для GUI)
        "--name=WeatherParser",  # Имя выходного файла
        "--clean",  # Очистка временных файлов
    ]

    # Добавляем данные: база данных и ресурсы GUI
    # Корректный формат для текущей ОС
    data_items = [("data/db/weather.db", "data/db"), ("src/gui/resources", "src/gui/resources")]
    for src, dst in data_items:
        if os.path.exists(src):
            data_arg = get_data_format(src, dst)
            pyinstaller_args.append(f"--add-data={data_arg}")
            print(f"Добавляем ресурсы: {src} -> {dst}")
        else:
            print(f"⚠️  Предупреждение: файл/папка не найден(а) {src}")

    # Скрытые импорты, которые PyInstaller может не обнаружить автоматически
    hidden_imports = [
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "sqlite3",
        "dotenv",
        "requests",
        "pandas",
        "src",  # Ваш собственный пакет
        "src.core",
        "src.database",
        "src.gui",
        "src.notifications",
        "src.utils",
    ]
    for imp in hidden_imports:
        pyinstaller_args.append(f"--hidden-import={imp}")

    # Ключевые настройки для корректной работы PyQt6
    pyinstaller_args.extend(
        [
            "--noconfirm",  # Не спрашивать подтверждения перезаписи
        ]
    )

    print("\nАргументы для PyInstaller:")
    for arg in pyinstaller_args:
        print(f"  {arg}")
    print("\nСборка может занять несколько минут...")

    try:
        # Запуск PyInstaller
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n✅ Сборка успешно завершена!")
        print(f"Исполняемый файл создан в папке: {os.path.abspath('dist')}")
        print("Файл: dist/WeatherParser" + (".exe" if platform.system() == "Windows" else ""))
    except Exception as e:
        print(f"\n❌ Ошибка во время сборки: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
