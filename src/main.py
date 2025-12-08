import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_current_weather():
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        base_url = os.getenv("OPENWEATHER_BASE_URL")
        city = os.getenv("DEFAULT_CITY", "Moscow")
        lang = os.getenv("DEFAULT_LANGUAGE", "ru")
        units = os.getenv("DEFAULT_UNITS", "metric")

        if not api_key:
            print("❌ Ошибка: OPENWEATHER_API_KEY не найден в .env файле")
            return

        url = f"{base_url}/weather"
        params = {"q": city, "appid": api_key, "lang": lang, "units": units}

        print("🌍 Запрашиваю погоду на сервере OpenWeatherMap...")

        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            print(f"✅ Текущая погода в городе {city}:")
            print(f"✅ Температура: {temp}°C")
            print(f"✅ Ощущается как: {feels_like}")
            print(f"✅ Описание: {description}")
            print(f"✅ Влажность: {humidity}%")
            print(f"✅ Скорость ветра: {wind_speed} м/с")
        elif response.status_code == 401:
            print("❌ Ошибка 401: Неверный API ключ")
        elif response.status_code == 404:
            print(f"❌ Ошибка 404: Город '{city}' не найден")
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"   Ответ: {response.text[:100]}...")

    except requests.exceptions.Timeout:
        print("❌ Таймаут: Превышено время ожидания ответа от сервера")
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка соединения: Проверьте интернет-подключение")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")


if __name__ == "__main__":
    get_current_weather()
