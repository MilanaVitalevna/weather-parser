"""Движок для генерации уведомлений на основе правил."""

from src.database.db_manager import db_manager
from src.database.models import IssuedNotification, WeatherRecord
from src.notifications.evaluator import ConditionEvaluator


class NotificationEngine:
    """Движок для обработки уведомлений."""

    def __init__(self):
        """Инициализирует движок уведомлений."""
        self.evaluator = ConditionEvaluator()

    def process_weather_data(self, weather_data: dict, response_time_ms: int = 0) -> tuple[int, list[str]]:
        """Обрабатывает данные о погоде, сохраняет в БД и генерирует уведомления.

        Args:
            weather_data: Словарь с данными о погоде
            response_time_ms: Время ответа API в миллисекундах

        Returns:
            Кортеж (ID сохраненной записи, список сообщений уведомлений)
        """
        # 1. Сохраняем запись в историю
        record = WeatherRecord(
            city=weather_data.get("city", ""),
            timestamp=weather_data.get("timestamp"),
            temperature=weather_data.get("temperature", 0),
            feels_like=weather_data.get("feels_like", 0),
            humidity=weather_data.get("humidity", 0),
            pressure=weather_data.get("pressure", 0),
            description=weather_data.get("description", ""),
            wind_speed=weather_data.get("wind_speed", 0),
            response_time_ms=response_time_ms,
        )

        history_id = db_manager.save_weather_record(record)

        # 2. Получаем активные правила
        rules = db_manager.get_active_notification_rules()
        notifications = []

        # 3. Проверяем каждое правило
        for rule in rules:
            try:
                if self.evaluator.evaluate(rule, weather_data):
                    message = self.evaluator.format_message(rule, weather_data)

                    # Сохраняем уведомление в БД
                    issued_notification = IssuedNotification(history_id=history_id, rule_id=rule.id, message=message)
                    db_manager.save_issued_notification(issued_notification)

                    notifications.append(message)

            except (ValueError, TypeError) as e:
                print(f"Ошибка при оценке правила {rule.name}: {e}")
                continue

        return history_id, notifications

    def get_recent_notifications(self, limit: int = 5) -> list[str]:
        """Получает последние уведомления.

        Args:
            limit: Максимальное количество уведомлений

        Returns:
            Список последних уведомлений
        """
        recent_records = db_manager.get_recent_records(limit=limit)
        if not recent_records:
            return []

        latest_record = recent_records[0]
        notifications = db_manager.get_notifications_for_record(latest_record.id)

        return [n.message for n in notifications]


# Глобальный экземпляр для использования
notification_engine = NotificationEngine()
