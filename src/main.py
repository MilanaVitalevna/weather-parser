"""Точка входа в приложение с поддержкой CLI и GUI."""

import argparse

from src.cli import main as cli_main
from src.gui.main_window import main as gui_main


def main() -> None:
    """Основная функция запуска приложения."""
    parser = argparse.ArgumentParser(description="Weather Parser Notifier")
    parser.add_argument("--gui", action="store_true", help="Запустить в графическом режиме (по умолчанию)")
    parser.add_argument("--cli", action="store_true", help="Запустить в консольном режиме")

    args = parser.parse_args()

    # По умолчанию запускаем GUI
    if args.cli:
        cli_main()
    else:
        gui_main()


if __name__ == "__main__":
    main()
