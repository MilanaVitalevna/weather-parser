"""Константы для GUI приложения."""

# Окно
WINDOW_TITLE = "🌤️ Weather Parser Notifier"
MAIN_TITLE = "Умный парсер погоды с уведомлениями"

# Размеры окна
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400
WINDOW_X = 100
WINDOW_Y = 100

# Тайминги
TIMER_DELAY_MS = 100  # Задержка для неблокирующего запроса

# Кнопки
BTN_GET_WEATHER = "🌍 Узнать погоду на сегодня"

# Статусы
STATUS_READY = "Готово к работе"
STATUS_SERVICE_INIT = "✅ Сервис погоды инициализирован"
STATUS_SERVICE_ERROR = "❌ Ошибка инициализации сервиса"
STATUS_LOADING = "🔄 Запрашиваю данные о погоде..."
STATUS_SUCCESS = "✅ Данные получены успешно"
STATUS_FETCH_ERROR = "❌ Ошибка при получении данных"

# Плейсхолдеры
PLACEHOLDER_WEATHER = "Здесь появится информация о погоде..."

# Ошибки
ERROR_SERVICE_NOT_INIT = "Сервис погоды не инициализирован"
ERROR_TITLE = "Ошибка"

# Форматы
WEATHER_TEMPLATE = """🌤 ПОГОДА В ГОРОДЕ {city}
══════════════════════════════════════════
🌡️ Температура:     {temperature}°C
🤔 Ощущается как:   {feels_like}°C
💧 Влажность:       {humidity}%
📊 Давление:        {pressure_mmhg} мм рт. ст. ({pressure_hpa} гПа)
☁️ Описание:        {description}
💨 Скорость ветра:  {wind_speed:.1f} м/с
══════════════════════════════════════════"""
