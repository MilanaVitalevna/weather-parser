"""Загрузка и проверка конфигурации приложения."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Настройки приложения."""

    # Обязательное поле (без значения по умолчанию)
    api_key: str

    # Поля со значениями по умолчанию
    base_url: str = "https://api.openweathermap.org/data/2.5/weather"
    city: str = "Moscow"
    language: str = "ru"
    units: str = "metric"
    timeout: int = 30


class ConfigLoader:
    """Загрузчик начальной настройки из переменных окружения ENV."""

    @staticmethod
    def load() -> Config:
        """Загружает и проверяет настройку."""
        api_key: str | None = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise ValueError("OPENWEATHER_API_KEY не найден в .env файле")

        # Разбираем значение timeout с проверкой на ошибки
        timeout_str: str = os.getenv("REQUEST_TIMEOUT", "30")
        try:
            timeout: int = int(timeout_str)
        except ValueError as err:
            raise ValueError(f"Некорректное значение timeout: '{timeout_str}'. Должно быть целым числом.") from err

        # Дополнительная проверка
        if timeout <= 0:
            raise ValueError(f"Таймаут должен быть положительным числом, получено: {timeout}")

        return Config(
            api_key=api_key,
            base_url=os.getenv(
                "OPENWEATHER_BASE_URL",
                "https://api.openweathermap.org/data/2.5/weather",
            ),
            city=os.getenv("DEFAULT_CITY", "Moscow"),
            language=os.getenv("DEFAULT_LANGUAGE", "ru"),
            units=os.getenv("DEFAULT_UNITS", "metric"),
            timeout=timeout,
        )
