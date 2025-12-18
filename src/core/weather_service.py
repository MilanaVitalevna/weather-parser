"""Сервис для координации получения данных о погоде."""

from src.core.api_client import OpenWeatherMapApiClient
from src.core.config_loader import Config, ConfigLoader
from src.core.data_parser import WeatherData, parse_openweathermap_response


class WeatherService:
    """Основной сервис для получения и обработки данных о погоде."""

    def __init__(self, config: Config | None = None):
        """Инициализирует сервис погоды.

        Args:
            config: Конфигурация приложения. Если None, загружается из .env
        """
        self.config = config or ConfigLoader.load()
        self.api_client = OpenWeatherMapApiClient(self.config)

    def get_weather(self, city: str | None = None) -> WeatherData:
        """Получает данные о погоде для указанного города.

        Args:
            city: Название города

        Returns:
            WeatherData: Структурированные данные о погоде

        Raises:
            ValueError: При ошибках конфигурации или парсинга
            RequestException: При ошибках сети или API
        """
        # Временная логика - пока не поддерживаем смену города через аргумент
        # TODO: Добавить поддержку смены города
        raw_json = self.api_client.fetch_weather_json()
        return parse_openweathermap_response(raw_json)
