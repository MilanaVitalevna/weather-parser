"""Консольная версия приложения."""

from requests.exceptions import RequestException

from src.core.weather_service import WeatherService
from src.utils.pressure_converter import convert_pressure_to_mmhg


def display_weather_cli(weather_data, notifications: list[str] | None = None) -> None:
    """Отображает данные о погоде в консоли."""
    pressure_mmhg = convert_pressure_to_mmhg(weather_data.pressure)

    print(f"\n🌤 ПОГОДА В ГОРОДЕ {weather_data.city.upper()}")
    print("=" * 50)
    print(f"🌡️ Температура:     {weather_data.temperature}°C")
    print(f"🤔 Ощущается как:   {weather_data.feels_like}°C")
    print(f"💧 Влажность:       {weather_data.humidity}%")
    print(f"📊 Давление:        {pressure_mmhg} мм рт. ст. ({weather_data.pressure} гПа)")
    print(f"☁️ Описание:        {weather_data.description}")
    print(f"💨 Скорость ветра:  {weather_data.wind_speed:.1f} м/с")
    print("=" * 50)

    if notifications:
        print(f"\n🔔 АКТИВНЫЕ РЕКОМЕНДАЦИИ ({len(notifications)}):")
        print("-" * 50)
        for i, notification in enumerate(notifications, 1):
            print(f"  {i}. {notification}")


def main() -> None:
    """Запуск консольной версии."""
    print("=" * 50)
    print("🌤️  Weather Parser Notifier (CLI Version)")
    print("=" * 50)

    try:
        service = WeatherService()
        print("🔧 Загрузка настроек приложения погоды...")
        print("🌍 Запрашиваю погоду на сервере OpenWeather...")
        print("🔍 Обработка и подготовка данных для вывода...")

        # Используем новый метод с уведомлениями
        weather_data, notifications = service.get_weather_with_notifications()
        display_weather_cli(weather_data, notifications)

    except ValueError as e:
        print(f"\n❌ Ошибка конфигурации или данных: {e}")
    except RequestException as e:
        print(f"\n❌ Ошибка при обращении к серверу погоды: {e}")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
