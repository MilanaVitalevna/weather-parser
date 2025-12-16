from requests.exceptions import RequestException

from src.api_client import OpenWeatherMapApiClient
from src.config_loader import Config, ConfigLoader
from src.data_parser import WeatherData, parse_openweathermap_response
from src.weather_display import display_error, display_weather


def get_current_weather():
    """
    Получает и отображает текущую погоду.
    Обрабатывает исключения на верхнем уровне.
    """
    try:
        # 1. Загрузка начальных настроек приложения из переменных окружения ENV
        print("🔧 Загрузка настроек приложения погоды...")
        config: Config = ConfigLoader.load()

        # 2. Получение полного списка неразобранных данных от API OpenWeatherMap
        print("🌍 Запрашиваю погоду на сервере OpenWeather...")
        api_client: OpenWeatherMapApiClient = OpenWeatherMapApiClient(config)
        raw_json: dict = api_client.fetch_weather_json()

        # 3. Отбор данных из полученного списка в подготовленный вид для вывода
        print("🔍 Обработка и подготовка данных для вывода...")
        weather_data: WeatherData = parse_openweathermap_response(raw_json)

        # 4. Вывод подготовленных данных для пользователя
        display_weather(weather_data)

    except ValueError as e:
        # Ошибки начальной настройки или разбора данных
        display_error(f"Ошибка конфигурации или данных: {e}")

    except RequestException as e:
        # Обработка всех ошибок сети или API OpenWeather
        display_error(f"Ошибка при обращении к серверу погоды: {e}")

    except Exception as e:
        # Все остальные непредвиденные ошибки
        display_error(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    get_current_weather()
