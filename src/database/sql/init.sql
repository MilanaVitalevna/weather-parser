-- Инициализация базы данных SQLite

-- Таблица: история запросов погоды
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
);

-- Таблица: правила уведомлений
-- Вставляем базовые правила уведомлений
INSERT OR IGNORE INTO notification_rules
(id, name, condition_type, operator, threshold_value, message_template, icon, priority) VALUES
(1, 'Холодно', 'temperature', 'lt', '5', '🧥 Наденьте куртку! На улице холодно ({temperature}°C)', '🧥', 1),
(2, 'Очень холодно', 'temperature', 'lt', '0', '❄️ Сильный мороз! Теплая одежда обязательна ({temperature}°C)', '❄️', 1),
(3, 'Жарко', 'temperature', 'gt', '25', '🥵 Жарко! Не забудьте воду и головной убор ({temperature}°C)', '🥵', 2),
(4, 'Дождь', 'description', 'contains', 'дождь', '☔ Возьмите зонт! {description}', '☔', 1),
(5, 'Сильный дождь', 'description', 'contains', 'ливень', '🌧️ Сильный дождь! Одевайтесь соответственно', '🌧️', 1),
(6, 'Снег', 'description', 'contains', 'снег', '⛄ Идет снег! Одевайтесь теплее', '⛄', 1),
(7, 'Сильный ветер', 'wind_speed', 'gt', '10', '💨 Сильный ветер ({wind_speed} м/с)! Будьте осторожны', '💨', 2),
(8, 'Высокая влажность', 'humidity', 'gt', '80', '💧 Высокая влажность ({humidity}%). Одежда сохнет медленно', '💧', 3),
(9, 'Низкое давление', 'pressure', 'lt', '730', '📉 Низкое давление ({pressure} мм рт.ст.). Метеозависимым быть осторожнее', '📉', 3);

-- Таблица: выданные уведомления (связь история-правила)
CREATE TABLE IF NOT EXISTS issued_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    history_id INTEGER NOT NULL,
    rule_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (history_id) REFERENCES weather_history(id) ON DELETE CASCADE,
    FOREIGN KEY (rule_id) REFERENCES notification_rules(id) ON DELETE CASCADE
);

-- Создаем индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_weather_history_timestamp ON weather_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_history_city ON weather_history(city);
CREATE INDEX IF NOT EXISTS idx_notification_rules_active ON notification_rules(is_active, priority);
CREATE INDEX IF NOT EXISTS idx_issued_notifications_history ON issued_notifications(history_id);

-- Вставляем базовые правила уведомлений
INSERT OR IGNORE INTO notification_rules
(name, condition_type, operator, threshold_value, message_template, icon, priority) VALUES
('Холодно', 'temperature', 'lt', '5', '🧥 Наденьте куртку! На улице холодно (+{value}°C)', '🧥', 1),
('Очень холодно', 'temperature', 'lt', '0', '❄️ Сильный мороз! Теплая одежда обязательна ({value}°C)', '❄️', 1),
('Жарко', 'temperature', 'gt', '25', '🥵 Жарко! Не забудьте воду и головной убор (+{value}°C)', '🥵', 2),
('Дождь', 'description', 'contains', 'дождь', '☔ Возьмите зонт! {description}', '☔', 1),
('Сильный дождь', 'description', 'contains', 'ливень', '🌧️ Сильный дождь! Одевайтесь соответственно', '🌧️', 1),
('Снег', 'description', 'contains', 'снег', '⛄ Идет снег! Одевайтесь теплее', '⛄', 1),
('Сильный ветер', 'wind_speed', 'gt', '10', '💨 Сильный ветер ({value} м/с)! Будьте осторожны', '💨', 2),
('Высокая влажность', 'humidity', 'gt', '80', '💧 Высокая влажность ({value}%). Одежда сохнет медленно', '💧', 3),
('Низкое давление', 'pressure', 'lt', '730', '📉 Низкое давление ({value} мм рт.ст.). Метеозависимым быть осторожнее', '📉', 3);
