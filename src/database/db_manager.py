"""Менеджер базы данных SQLite."""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from src.database.models import IssuedNotification, NotificationRule, WeatherRecord


class DatabaseManager:
    """Управление базой данных SQLite для приложения погоды."""

    def __init__(self, db_path: str | None = None):
        """Инициализирует менеджер базы данных.

        Args:
            db_path: Путь к файлу базы данных. Если None, используется data/db/weather.db
        """
        if db_path is None:
            # Создаем директорию data/db если ее нет
            base_dir = Path(__file__).parent.parent.parent
            db_dir = base_dir / "data" / "db"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / "weather.db"
        else:
            self.db_path = Path(db_path)

        self._init_database()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Контекстный менеджер для получения соединения с БД."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
        conn.execute("PRAGMA foreign_keys = ON")  # Включаем внешние ключи
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Инициализирует базу данных, создает таблицы если их нет."""
        with self._get_connection() as conn:
            # Таблица истории запросов погоды
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    temperature REAL NOT NULL,
                    feels_like REAL NOT NULL,
                    humidity INTEGER NOT NULL,
                    pressure INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    wind_speed REAL NOT NULL,
                    response_time_ms INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица правил уведомлений
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notification_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    condition_type TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    threshold_value TEXT NOT NULL,
                    message_template TEXT NOT NULL,
                    icon TEXT,
                    priority INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица выданных уведомлений
            conn.execute("""
                CREATE TABLE IF NOT EXISTS issued_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    history_id INTEGER NOT NULL,
                    rule_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (history_id) REFERENCES weather_history(id) ON DELETE CASCADE,
                    FOREIGN KEY (rule_id) REFERENCES notification_rules(id) ON DELETE CASCADE
                )
            """)

            # Создаем индексы
            conn.execute("CREATE INDEX IF NOT EXISTS idx_weather_history_timestamp ON weather_history(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_weather_history_city ON weather_history(city)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_notification_rules_active ON notification_rules(is_active, priority)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_issued_notifications_history ON issued_notifications(history_id)"
            )

            # Вставляем базовые правила уведомлений
            self._insert_base_rules(conn)

    def _insert_base_rules(self, conn: sqlite3.Connection) -> None:
        """Вставляет базовые правила уведомлений в базу данных."""
        base_rules = [
            # Базовые температурные правила
            (1, "Холодно", "temperature", "lt", "5", "🧥 Наденьте куртку! На улице холодно ({temperature}°C)", "🧥", 1),
            (
                2,
                "Очень холодно",
                "temperature",
                "lt",
                "0",
                "❄️ Сильный мороз! Теплая одежда обязательна ({temperature}°C)",
                "❄️",
                1,
            ),
            (
                3,
                "Жарко",
                "temperature",
                "gt",
                "25",
                "🥵 Жарко! Не забудьте воду и головной убор ({temperature}°C)",
                "🥵",
                2,
            ),
            # Погодные явления
            (4, "Дождь", "description", "contains", "дождь", "☔ Возьмите зонт! {description}", "☔", 1),
            (
                5,
                "Сильный дождь",
                "description",
                "contains",
                "ливень",
                "🌧️ Сильный дождь! Одевайтесь соответственно",
                "🌧️",
                1,
            ),
            (6, "Снег", "description", "contains", "снег", "⛄ Идет снег! Одевайтесь теплее", "⛄", 1),
            (7, "Туман", "description", "contains", "туман", "🌫️ Туман! Будьте осторожны на дороге", "🌫️", 2),
            (8, "Гроза", "description", "contains", "гроза", "⛈️ Гроза! Оставайтесь в помещении", "⛈️", 1),
            # Ветер
            (
                9,
                "Сильный ветер",
                "wind_speed",
                "gt",
                "10",
                "💨 Сильный ветер ({wind_speed} м/с)! Будьте осторожны",
                "💨",
                2,
            ),
            (
                10,
                "Очень сильный ветер",
                "wind_speed",
                "gt",
                "15",
                "🌪️ Очень сильный ветер ({wind_speed} м/с)! Лучше остаться дома",
                "🌪️",
                1,
            ),
            # Влажность
            (
                11,
                "Высокая влажность",
                "humidity",
                "gt",
                "80",
                "💧 Высокая влажность ({humidity}%). Одежда сохнет медленно",
                "💧",
                3,
            ),
            (12, "Очень сухо", "humidity", "lt", "30", "🏜️ Очень сухо ({humidity}%). Пейте больше воды", "🏜️", 3),
            # Давление
            (
                13,
                "Низкое давление",
                "pressure",
                "lt",
                "730",
                "📉 Низкое давление ({pressure} мм рт.ст.). Метеозависимым быть осторожнее",
                "📉",
                3,
            ),
            (14, "Высокое давление", "pressure", "gt", "780", "📈 Высокое давление ({pressure} мм рт.ст.)", "📈", 3),
            # Комбинированные условия (через специальные правила)
            (
                15,
                "Холодно + Ветер",
                "feels_like",
                "lt",
                "-5",
                "🥶 Холодно с ветром! Ощущается как {feels_like}°C. Оденьтесь теплее!",
                "🥶",
                1,
            ),
            (
                16,
                "Жарко + Влажность",
                "temperature_humidity",
                "gt",
                "75",
                "🔥 Душно и жарко! {temperature}°C и {humidity}% влажности",
                "🔥",
                2,
            ),
        ]

        for rule in base_rules:
            try:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO notification_rules
                    (id, name, condition_type, operator, threshold_value, message_template, icon, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    rule,
                )
            except sqlite3.IntegrityError:
                # Правило уже существует
                continue

    def save_weather_record(self, record: WeatherRecord) -> int:
        """Сохраняет запись о погоде в базу данных.

        Args:
            record: Запись о погоде

        Returns:
            ID сохраненной записи
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO weather_history
                (city, timestamp, temperature, feels_like, humidity, pressure,
                 description, wind_speed, response_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    record.city,
                    record.timestamp or datetime.now(),
                    record.temperature,
                    record.feels_like,
                    record.humidity,
                    record.pressure,
                    record.description,
                    record.wind_speed,
                    record.response_time_ms,
                ),
            )
            return cursor.lastrowid

    def get_recent_records(self, limit: int = 10) -> list[WeatherRecord]:
        """Получает последние записи о погоде.

        Args:
            limit: Максимальное количество записей (0 = все записи)

        Returns:
            Список последних записей
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if limit == 0:
                # Получаем все записи
                cursor.execute("""
                    SELECT * FROM weather_history
                    ORDER BY timestamp DESC
                """)
            else:
                cursor.execute(
                    """
                    SELECT * FROM weather_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            records = []
            for row in cursor.fetchall():
                records.append(
                    WeatherRecord(
                        id=row["id"],
                        city=row["city"],
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        temperature=row["temperature"],
                        feels_like=row["feels_like"],
                        humidity=row["humidity"],
                        pressure=row["pressure"],
                        description=row["description"],
                        wind_speed=row["wind_speed"],
                        response_time_ms=row["response_time_ms"],
                        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
                    )
                )
            return records

    def get_active_notification_rules(self) -> list[NotificationRule]:
        """Получает все активные правила уведомлений.

        Returns:
            Список активных правил
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notification_rules
                WHERE is_active = 1
                ORDER BY priority, id
            """)

            rules = []
            for row in cursor.fetchall():
                rules.append(
                    NotificationRule(
                        id=row["id"],
                        name=row["name"],
                        condition_type=row["condition_type"],
                        operator=row["operator"],
                        threshold_value=row["threshold_value"],
                        message_template=row["message_template"],
                        icon=row["icon"],
                        priority=row["priority"],
                        is_active=bool(row["is_active"]),
                        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
                    )
                )
            return rules

    def save_issued_notification(self, notification: IssuedNotification) -> int:
        """Сохраняет выданное уведомление.

        Args:
            notification: Выданное уведомление

        Returns:
            ID сохраненного уведомления
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO issued_notifications (history_id, rule_id, message)
                VALUES (?, ?, ?)
            """,
                (notification.history_id, notification.rule_id, notification.message),
            )
            return cursor.lastrowid

    def get_notifications_for_record(self, history_id: int) -> list[IssuedNotification]:
        """Получает все уведомления для конкретной записи.

        Args:
            history_id: ID записи в истории

        Returns:
            Список уведомлений
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT inot.*, nr.icon, nr.priority
                FROM issued_notifications inot
                JOIN notification_rules nr ON inot.rule_id = nr.id
                WHERE inot.history_id = ?
                ORDER BY nr.priority, inot.created_at
            """,
                (history_id,),
            )

            notifications = []
            for row in cursor.fetchall():
                notifications.append(
                    IssuedNotification(
                        id=row["id"],
                        history_id=row["history_id"],
                        rule_id=row["rule_id"],
                        message=row["message"],
                        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
                    )
                )
            return notifications

    def get_record_count(self) -> int:
        """Получает общее количество записей в истории.

        Returns:
            Количество записей
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM weather_history")
            return cursor.fetchone()["count"]

    def clear_history(self) -> bool:
        """Очищает всю историю запросов.

        Returns:
            True если успешно, False если ошибка
        """
        try:
            with self._get_connection() as conn:
                # Удаляем данные в правильном порядке (сначала дочерние таблицы)
                conn.execute("DELETE FROM issued_notifications")
                conn.execute("DELETE FROM weather_history")

            # VACUUM должен быть вне транзакции
            conn = sqlite3.connect(self.db_path)
            conn.execute("VACUUM")
            conn.close()

            return True

        except Exception as e:
            print(f"Ошибка очистки истории: {e}")
            return False


# Глобальный экземпляр для использования во всем приложении
db_manager = DatabaseManager()
