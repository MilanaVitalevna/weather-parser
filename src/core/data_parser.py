"""Разбор данных от OpenWeatherMap API."""

from dataclasses import dataclass
from typing import Any


@dataclass
class WeatherData:
    """Выбранные данные о погоде для последующего вывода клиенту."""

    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    description: str
    wind_speed: float
    city: str


def parse_openweathermap_response(json_response: dict[str, Any]) -> WeatherData:
    """
    Отбирает нужные погодные данные из сырого JSON.

    Args:
        json_response: Словарь с погодными данными от API OpenWeatherMap.

    Returns:
        WeatherData объект с отобранными погодными данными.

    Raises:
        ValueError: Если получены непредусмотренные данные.
    """
    try:
        return WeatherData(
            temperature=json_response["main"]["temp"],
            feels_like=json_response["main"]["feels_like"],
            humidity=json_response["main"]["humidity"],
            pressure=json_response["main"]["pressure"],
            description=json_response["weather"][0]["description"],
            wind_speed=json_response["wind"]["speed"],
            city=json_response["name"],
        )
    except (KeyError, IndexError) as e:
        raise ValueError(f"Непредусмотренные данные от API: {e}") from e
