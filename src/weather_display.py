"""Модуль для отображения данных о погоде."""

from src.data_parser import WeatherData
from src.utils.pressure_converter import convert_pressure_to_mmhg


def display_weather(weather_data: WeatherData) -> None:
    """
    Выводит данные о погоде в консоль для пользователя.

    Args:
        weather_data: Объект WeatherData с отобранными данными о погоде
    """

    # Преобразуем давление для общепринятого формата в России
    pressure_mmhg: int = convert_pressure_to_mmhg(weather_data.pressure)

    print(f"\n🌤 Погода в городе {weather_data.city}:")
    print("=" * 30)
    print(f"Температура:    {weather_data.temperature}°C")
    print(f"Ощущается как:  {weather_data.feels_like}°C")
    print(f"Влажность:      {weather_data.humidity}%")
    print(f"Давление:       {pressure_mmhg} мм рт. ст. ({weather_data.pressure} гПа)")
    print(f"Описание:       {weather_data.description}")
    print(f"Скорость ветра: {weather_data.wind_speed:>.1f} м/с")
    print("=" * 30)


def display_error(error_message: str) -> None:
    """
    Выводит сообщение об ошибке.

    Args:
        error_message: Текст ошибки
    """
    print(f"\n❌ Ошибка: {error_message}")
