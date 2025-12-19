"""Оценщик условий для правил уведомлений."""

from typing import Any

from src.database.models import NotificationRule
from src.utils.pressure_converter import convert_pressure_to_mmhg


class ConditionEvaluator:
    """Оценивает условия правил уведомлений."""

    @staticmethod
    def evaluate(rule: NotificationRule, weather_data: dict[str, Any]) -> bool:
        """Оценивает, выполняется ли правило для данных о погоде.

        Args:
            rule: Правило уведомления
            weather_data: Словарь с данными о погоде

        Returns:
            True если условие выполняется, иначе False
        """
        # Специальные комбинированные условия
        if rule.condition_type == "feels_like":
            # Холодно + Ветер (ощущаемая температура)
            value = weather_data.get("feels_like", 0)
            threshold = float(rule.threshold_value)
            return value < threshold

        elif rule.condition_type == "temperature_humidity":
            # Жарко + Влажность (температура * влажность / 100)
            temp = weather_data.get("temperature", 0)
            humidity = weather_data.get("humidity", 0)
            value = temp * humidity / 100
            threshold = float(rule.threshold_value)
            return value > threshold

        # Базовые условия
        return ConditionEvaluator._evaluate_basic_condition(rule, weather_data)

    @staticmethod
    def _evaluate_basic_condition(rule: NotificationRule, weather_data: dict[str, Any]) -> bool:
        """Оценивает базовые условия."""
        # Получаем значение из данных о погоде
        if rule.condition_type == "temperature":
            value = weather_data.get("temperature", 0)
            threshold = float(rule.threshold_value)
        elif rule.condition_type == "humidity":
            value = weather_data.get("humidity", 0)
            threshold = float(rule.threshold_value)
        elif rule.condition_type == "wind_speed":
            value = weather_data.get("wind_speed", 0)
            threshold = float(rule.threshold_value)
        elif rule.condition_type == "pressure":
            # Преобразуем давление в мм рт.ст. для сравнения
            pressure_hpa = weather_data.get("pressure", 0)
            value = convert_pressure_to_mmhg(pressure_hpa)
            threshold = float(rule.threshold_value)
        elif rule.condition_type == "description":
            value = str(weather_data.get("description", "")).lower()
            threshold = rule.threshold_value.lower()
        else:
            return False

        # Применяем оператор
        if rule.operator == "gt":
            return value > threshold
        elif rule.operator == "lt":
            return value < threshold
        elif rule.operator == "gte":
            return value >= threshold
        elif rule.operator == "lte":
            return value <= threshold
        elif rule.operator == "eq":
            return value == threshold
        elif rule.operator == "contains":
            return threshold in value
        else:
            return False

    @staticmethod
    def format_message(rule: NotificationRule, weather_data: dict[str, Any]) -> str:
        """Форматирует сообщение уведомления, заменяя плейсхолдеры.

        Args:
            rule: Правило уведомления
            weather_data: Словарь с данными о погоде

        Returns:
            Отформатированное сообщение
        """
        message = rule.message_template

        # Преобразуем давление если нужно
        pressure_mmhg = convert_pressure_to_mmhg(weather_data.get("pressure", 0))

        # Заменяем общие плейсхолдеры
        placeholders = {
            "{temperature}": f"{weather_data.get('temperature', 0):.1f}",
            "{feels_like}": f"{weather_data.get('feels_like', 0):.1f}",
            "{humidity}": str(weather_data.get("humidity", 0)),
            "{pressure}": str(pressure_mmhg),
            "{wind_speed}": f"{weather_data.get('wind_speed', 0):.1f}",
            "{description}": str(weather_data.get("description", "")),
            "{city}": str(weather_data.get("city", "")),
        }

        for placeholder, replacement in placeholders.items():
            message = message.replace(placeholder, replacement)

        return message
