"""Сервис для координации получения данных о погоде."""

import time

from src.core.api_client import OpenWeatherMapApiClient
from src.core.config_loader import Config, ConfigLoader
from src.core.data_parser import WeatherData, parse_openweathermap_response
from src.notifications.engine import notification_engine


class WeatherService:
    """Основной сервис для получения и обработки данных о погоде."""

    def __init__(self, config: Config | None = None):
        """Инициализирует сервис погоды.

        Args:
            config: Конфигурация приложения. Если None, загружается из .env
        """
        self.config = config or ConfigLoader.load()
        self.api_client = OpenWeatherMapApiClient(self.config)

    def get_weather_with_notifications(self) -> tuple[WeatherData, list[str]]:
        """Получает данные о погоде и генерирует уведомления.

        Returns:
            Кортеж (WeatherData, список уведомлений)

        Raises:
            ValueError: При ошибках конфигурации или парсинга
            requests.exceptions.RequestException: При ошибках сети или API
        """
        start_time = time.time()

        try:
            # Получаем сырые данные
            raw_json = self.api_client.fetch_weather_json()

            # Парсим данные
            weather_data = parse_openweathermap_response(raw_json)

            # Вычисляем время ответа
            response_time = int((time.time() - start_time) * 1000)

            # Преобразуем WeatherData в словарь для движка уведомлений
            weather_dict = {
                "city": weather_data.city,
                "temperature": weather_data.temperature,
                "feels_like": weather_data.feels_like,
                "humidity": weather_data.humidity,
                "pressure": weather_data.pressure,
                "description": weather_data.description.lower(),  # Для проверки contains
                "wind_speed": weather_data.wind_speed,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Обрабатываем уведомления
            history_id, notifications = notification_engine.process_weather_data(weather_dict, response_time)

            print(f"✅ Запрос сохранен в истории (ID: {history_id})")
            print(f"🔔 Сгенерировано уведомлений: {len(notifications)}")

            return weather_data, notifications

        except Exception as e:
            print(f"❌ Ошибка при получении погоды: {e}")
            raise

    def get_weather(self) -> WeatherData:
        """Получает данные о погоде (старый метод для обратной совместимости).

        Returns:
            WeatherData: Структурированные данные о погоде
        """
        weather_data, _ = self.get_weather_with_notifications()
        return weather_data
