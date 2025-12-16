"""Служба для работы с OpenWeatherMap API."""

import requests
from requests import Response

from src.config_loader import Config


class OpenWeatherMapApiClient:
    """Служба для получения полного списка неразобранных данных о погоде из API."""

    def __init__(self, config: Config):
        self.config = config

    def fetch_weather_json(self) -> dict:
        """
        Запрашивает данные о погоде и возвращает JSON полного списка неразобранных данных о погоде.

        Returns:
            Словарь с неразобранными данными от API OpenWeatherMap.
        """
        params = {
            "q": self.config.city,
            "appid": self.config.api_key,
            "lang": self.config.language,
            "units": self.config.units,
        }

        response: Response = requests.get(self.config.base_url, params=params, timeout=self.config.timeout)

        # Проверяет статус ответа: при ошибках HTTP (4xx, 5xx) выбрасываем исключение HTTPError
        response.raise_for_status()

        return response.json()
