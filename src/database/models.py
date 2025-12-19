"""Модели данных для базы данных."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeatherRecord:
    """Запись о погоде в истории."""

    id: int | None = None
    city: str = ""
    timestamp: datetime = None
    temperature: float = 0.0
    feels_like: float = 0.0
    humidity: int = 0
    pressure: int = 0
    description: str = ""
    wind_speed: float = 0.0
    response_time_ms: int = 0
    created_at: datetime | None = None


@dataclass
class NotificationRule:
    """Правило для генерации уведомлений."""

    id: int | None = None
    name: str = ""
    condition_type: str = ""  # temperature, humidity, wind, description, pressure
    operator: str = ""  # gt, lt, gte, lte, eq, contains
    threshold_value: str = ""  # Пороговое значение
    message_template: str = ""
    icon: str = ""
    priority: int = 1  # 1-высокий, 2-средний, 3-низкий
    is_active: bool = True
    created_at: datetime | None = None


@dataclass
class IssuedNotification:
    """Выданное уведомление для конкретного запроса."""

    id: int | None = None
    history_id: int = 0
    rule_id: int = 0
    message: str = ""
    created_at: datetime | None = None
