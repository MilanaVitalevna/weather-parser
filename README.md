# 🌤️ Weather Parser Notifier

Умный парсер погоды с персонализированными уведомлениями на Python.

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![UV](https://img.shields.io/badge/uv-0.1+-orange.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/ruff-0.1+-red.svg)](https://github.com/astral-sh/ruff)

## ✨ Особенности

- 📡 Получение актуальных данных о погоде с OpenWeatherMap API
- 🤖 Интеллектуальные уведомления на основе погодных условий
- 🎯 Персонализированные рекомендации
- ⚙️ Гибкая конфигурация через `.env` файл
- 🧪 Покрытие тестами
- 🚀 Современный стек разработки: uv, ruff

## 🚀 Быстрый старт

### 🛠️ Предварительные требования

- Python 3.12+
- [UV](https://github.com/astral-sh/uv)
- API ключ от [OpenWeatherMap](https://openweathermap.org/api)

### 📦 Управление зависимостями и установка

Проект следует современным стандартам Python:

- **`pyproject.toml`** — единый файл конфигурации проекта (стандартизирован PEP 518, 621, 660), который заменяет
  устаревшие `setup.py` и `requirements.txt`.
- **`uv.lock`** — автоматически создаваемый файл с точными версиями всех зависимостей для воспроизводимости сборки.

**Быстрая установка:**

```bash
make install # если make не установлен, тогда напрямую - uv sync
```

Файл `requirements.txt` всегда может быть сгенерирован для обратной совместимости:

```bash
uv pip compile pyproject.toml --output-file=requirements.txt
```

### 🔧 Конфигурация

Создайте файл `.env` на основе `.env.example`

### ▶️ Запуск приложения

```bash
# запуск графической версии
make run # если make не установлен, тогда напрямую - uv run python -m src.main

# запуск консольной версии
make run-cli # если make не установлен, тогда напрямую - uv run weather-cli
```

## 📁 Архитектура проекта

```text
weather-parser-notifier/
├── data/
│   └── db/
│       └── weather.db
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── config_loader.py
│   │   ├── data_parser.py
│   │   └── weather_service.py
│   ├── database/
│   │   ├── sql/
│   │   │   └── init.sql
│   │   ├── __init__.py
│   │   ├── db_manager.py
│   │   └── models.py
│   ├── gui/
│   │   ├── resources/
│   │   │   ├── backgrounds/
│   │   │   │   └── bg.png
│   │   │   └── styles/
│   │   │       └── main.qss
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── history_manager.py
│   │   ├── main_window.py
│   │   └── resource_manager.py
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── evaluator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── pressure_converter.py
│   ├── __init__.py
│   ├── cli.py
│   └── main.py
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── Makefile
├── pyproject.toml
├── README.md
├── requirements.txt
└── uv.lock
```

## 🙏 Благодарности

- **[OpenWeatherMap](https://openweathermap.org/)** — за предоставление качественного и бесплатного API с погодными
  данными для разработчиков
- **[Astral](https://astral.sh/)** — за создание невероятно быстрых и эффективных инструментов для экосистемы Python:
    - **[uv](https://github.com/astral-sh/uv)** — сверхбыстрый менеджер пакетов и инсталлятор на Rust
    - **[Ruff](https://github.com/astral-sh/ruff)** — невероятно быстрый линтер на Rust, заменивший 10+ отдельных
      инструментов

---

**Примечание:** Этот проект находится в активной разработке. Функционал и API могут меняться.
Мы приветствуем вклады сообщества через Issues и Pull Requests!
