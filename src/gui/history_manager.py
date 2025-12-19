"""Менеджер для работы с историей запросов."""

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from src.database.db_manager import db_manager
from src.utils.pressure_converter import convert_pressure_to_mmhg


class HistoryManager:
    """Управление историей запросов погоды."""

    @staticmethod
    def get_recent_history(limit: int = 5) -> list[dict[str, Any]]:
        """
        Получает последние записи истории.

        Args:
            limit: Максимальное количество записей (0 = все записи)

        Returns:
            Список словарей с данными для отображения
        """
        if limit == 0:
            records = db_manager.get_recent_records(limit=1000)
        else:
            records = db_manager.get_recent_records(limit=limit)

        formatted_records = []
        for record in records:
            # Форматируем время
            time_str = record.timestamp.strftime("%d.%m %H:%M") if record.timestamp else "Н/Д"

            # Форматируем температуру с иконкой
            temp_str = f"{record.temperature:+.1f}°C"
            temp_icon = ""
            if record.temperature < 0:
                temp_icon = "🔵 "  # Синий кружок для мороза
            elif record.temperature > 25:
                temp_icon = "🔴 "  # Красный кружок для жары

            # Форматируем описание погоды с иконкой
            weather_icon = HistoryManager._get_weather_icon(record.description)
            weather_text = f"{weather_icon} {record.description}"

            formatted_records.append(
                {
                    "id": record.id,
                    "time": time_str,
                    "temperature": f"{temp_icon}{temp_str}",
                    "temperature_raw": record.temperature,  # Для сортировки и обработки
                    "description": weather_text,
                    "full_record": record,
                }
            )

        return formatted_records

    @staticmethod
    def _get_weather_icon(description: str) -> str:
        """
        Возвращает иконку для описания погоды.

        Args:
            description: Описание погоды

        Returns:
            Строка с иконкой
        """
        desc_lower = description.lower()

        if "ясно" in desc_lower or "солнечно" in desc_lower:
            return "☀️"
        elif "облачно" in desc_lower:
            return "☁️"
        elif "дождь" in desc_lower:
            if "ливень" in desc_lower or "сильный" in desc_lower:
                return "🌧️"
            return "🌦️"
        elif "снег" in desc_lower:
            return "❄️"
        elif "туман" in desc_lower:
            return "🌫️"
        elif "гроза" in desc_lower or "гроз" in desc_lower:
            return "⛈️"
        elif "ветер" in desc_lower:
            return "💨"
        elif "пасмурно" in desc_lower:
            return "☁️"
        else:
            return "🌤️"

    @staticmethod
    def get_total_count() -> int:
        """
        Получает общее количество записей в истории.

        Returns:
            Количество записей
        """
        return db_manager.get_record_count()

    @staticmethod
    def clear_history() -> bool:
        """
        Очищает всю историю запросов.

        Returns:
            True если успешно, False если ошибка
        """
        try:
            db_manager.clear_history()
            return True
        except Exception as e:
            print(f"Ошибка очистки истории: {e}")
            return False

    @staticmethod
    def _get_export_directory() -> Path:
        """
        Возвращает путь к директории для экспорта.
        Создает директорию если ее нет.

        Returns:
            Path: Путь к директории экспорта
        """
        # Определяем базовую директорию
        base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent.parent

        # Создаем директорию data/exports
        export_dir = base_dir / "data" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        return export_dir

    @staticmethod
    def export_to_csv(filename: str | None = None) -> tuple[bool, str]:
        """
        Экспортирует историю в CSV файл в папку data/exports.

        Args:
            filename: Имя файла (если None, генерируется автоматически)

        Returns:
            Кортеж (успех, сообщение)
        """
        try:
            # Получаем директорию для экспорта
            export_dir = HistoryManager._get_export_directory()

            # Генерируем имя файла если не предоставлено
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"weather_history_{timestamp}.csv"

            # Полный путь к файлу
            filepath = export_dir / filename

            # Получаем все записи из БД напрямую
            records = db_manager.get_recent_records(limit=0)

            if not records:
                return False, "Нет данных для экспорта"

            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                # Заголовки
                fieldnames = [
                    "ID",
                    "Город",
                    "Время",
                    "Температура (°C)",
                    "Ощущается как (°C)",
                    "Влажность (%)",
                    "Давление (гПа)",
                    "Давление (мм рт.ст.)",
                    "Описание",
                    "Скорость ветра (м/с)",
                    "Время ответа (мс)",
                    "Дата создания",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                # Данные
                for record in records:
                    # Преобразуем давление в мм рт.ст.
                    pressure_mmhg = convert_pressure_to_mmhg(record.pressure)

                    writer.writerow(
                        {
                            "ID": record.id,
                            "Город": record.city,
                            "Время": record.timestamp.strftime("%Y-%m-%d %H:%M:%S") if record.timestamp else "",
                            "Температура (°C)": f"{record.temperature:.1f}",
                            "Ощущается как (°C)": f"{record.feels_like:.1f}",
                            "Влажность (%)": str(record.humidity),
                            "Давление (гПа)": str(record.pressure),
                            "Давление (мм рт.ст.)": f"{pressure_mmhg:.1f}",
                            "Описание": record.description,
                            "Скорость ветра (м/с)": f"{record.wind_speed:.1f}",
                            "Время ответа (мс)": str(record.response_time_ms),
                            "Дата создания": record.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if record.created_at
                            else "",
                        }
                    )

            # Возвращаем успех и путь к файлу
            return True, str(filepath)

        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False, f"Ошибка экспорта: {str(e)}"
