"""
Простой менеджер ресурсов для GUI приложения.
Работает как из исходников, так и из упакованного приложения (exe).
"""

import sys
from pathlib import Path


def _get_base_path() -> Path:
    """
    Возвращает базовый путь в зависимости от способа запуска.

    Returns:
        Path: Базовый путь для поиска ресурсов
    """
    # PyInstaller создает временную папку _MEIPASS
    if getattr(sys, "frozen", False):
        # noinspection PyProtectedMember
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)  # type: ignore[attr-defined]
        return Path(sys.executable).parent

    # Запуск из исходников
    return Path(__file__).parent.parent.parent


def get_resource_path(relative_path: str) -> Path:
    """
    Возвращает путь к ресурсу.

    Args:
        relative_path: Относительный путь (например: 'src/gui/resources/styles/main.qss')

    Returns:
        Path: Абсолютный путь к ресурсу
    """
    return _get_base_path() / relative_path


def load_stylesheet(style_name: str = "main") -> str:
    """
    Загружает QSS стили с заменой transparent на none.

    Args:
        style_name: Имя стиля (без расширения .qss)

    Returns:
        Строка с CSS стилями или резервные стили
    """
    try:
        style_path = get_resource_path(f"src/gui/resources/styles/{style_name}.qss")
        qss_content = style_path.read_text(encoding="utf-8")

        # Заменяем transparent для совместимости со всеми версиями Qt
        qss_content = qss_content.replace("transparent", "none")

        print(f"✅ Стиль '{style_name}' загружен")
        return qss_content

    except Exception as e:
        print(f"⚠️ Ошибка загрузки стиля '{style_name}': {e}")
        # Резервные стили
        return """
        QMainWindow {
            font-family: "Segoe UI", "Arial", sans-serif;
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QLabel { background: none; }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
        }
        QPushButton:hover { background-color: #45a049; }
        QPushButton:disabled { background-color: #666666; color: #aaaaaa; }
        QTextEdit {
            background-color: #393939;
            color: #E3E3E3;
            border: 2px solid #555555;
            border-radius: 5px;
            font-family: "Monospace", "Courier New";
        }
        QProgressBar {
            background-color: #333333;
            border: 1px solid #555555;
            border-radius: 3px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 3px;
        }
        """


def get_background_url(bg_name: str = "bg") -> str | None:
    """
    Возвращает URL фона для QSS или None.

    Args:
        bg_name: Имя фонового изображения (без расширения)

    Returns:
        Строка для QSS url() или None если фон не найден
    """
    try:
        bg_path = get_resource_path(f"src/gui/resources/backgrounds/{bg_name}.png")
        if bg_path.exists():
            bg_url = bg_path.as_posix().replace(" ", "%20")
            print(f"✅ Фон '{bg_name}' загружен")
            return f"url({bg_url})"
    except Exception as e:
        print(f"⚠️ Фон '{bg_name}' не загружен: {e}")

    return None
