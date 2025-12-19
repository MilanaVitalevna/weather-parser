"""Главное окно приложения."""

import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.data_parser import WeatherData
from src.core.weather_service import WeatherService
from src.gui.constants import (
    BTN_CLEAR_HISTORY,
    BTN_EXPORT_HISTORY,
    BTN_GET_WEATHER,
    ERROR_SERVICE_NOT_INIT,
    ERROR_TITLE,
    HISTORY_COLUMN_WIDTHS,
    HISTORY_COLUMNS,
    HISTORY_EMPTY,
    HISTORY_TITLE,
    MAIN_TITLE,
    PLACEHOLDER_WEATHER,
    STATUS_FETCH_ERROR,
    STATUS_LOADING,
    STATUS_READY,
    STATUS_SERVICE_ERROR,
    STATUS_SERVICE_INIT,
    STATUS_SUCCESS,
    TIMER_DELAY_MS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_X,
    WINDOW_Y,
)
from src.gui.history_manager import HistoryManager
from src.gui.resource_manager import get_background_url, load_stylesheet


class WeatherWindow(QMainWindow):
    """Главное окно приложения погоды."""

    def __init__(self):
        super().__init__()
        self.weather_service: WeatherService | None = None
        self.history_manager = HistoryManager()

        # Виджеты
        self.central_widget: QWidget | None = None
        self.title_label: QLabel | None = None
        self.get_weather_btn: QPushButton | None = None
        self.progress_bar: QProgressBar | None = None
        self.weather_output: QTextEdit | None = None
        self.status_label: QLabel | None = None

        # Новые виджеты для истории
        self.history_group: QGroupBox | None = None
        self.history_table: QTableWidget | None = None
        self.history_status: QLabel | None = None
        self.btn_clear_history: QPushButton | None = None
        self.btn_export_history: QPushButton | None = None

        self.init_ui()
        self.init_weather_service()
        self.load_history()  # Загружаем историю при старте

    def init_ui(self) -> None:
        """Инициализирует пользовательский интерфейс."""
        self.setup_main_window()
        self.create_widgets()
        self.setup_layout()
        self.setup_styles_and_background()
        self.setup_connections()
        self.setup_cursors()

    def setup_main_window(self) -> None:
        """Настраивает основное окно приложения."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

    def create_widgets(self) -> None:
        """Создает все виджеты окна."""
        self.central_widget = QWidget()
        self.title_label = QLabel(MAIN_TITLE)
        self.get_weather_btn = QPushButton(BTN_GET_WEATHER)
        self.progress_bar = QProgressBar()
        self.weather_output = QTextEdit()
        self.status_label = QLabel(STATUS_READY)

        # Виджеты истории
        self.history_group = QGroupBox(HISTORY_TITLE)
        self.history_table = QTableWidget()
        self.history_status = QLabel(HISTORY_EMPTY)
        self.btn_clear_history = QPushButton(BTN_CLEAR_HISTORY)
        self.btn_export_history = QPushButton(BTN_EXPORT_HISTORY)

    def setup_layout(self) -> None:
        """Настраивает компоновку виджетов."""
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Основная секция
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.get_weather_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.weather_output)
        main_layout.addWidget(self.status_label)

        # Секция истории
        self.setup_history_layout()
        main_layout.addWidget(self.history_group)

        self.setCentralWidget(self.central_widget)

    def setup_history_layout(self) -> None:
        """Настраивает компоновку секции истории."""
        history_layout = QVBoxLayout(self.history_group)

        # Настраиваем таблицу
        self.history_table.setColumnCount(len(HISTORY_COLUMNS))
        self.history_table.setHorizontalHeaderLabels(HISTORY_COLUMNS)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.verticalHeader().setVisible(False)

        # Устанавливаем ширину колонок
        for i, width in enumerate(HISTORY_COLUMN_WIDTHS):
            self.history_table.setColumnWidth(i, width)

        # Автоматическое растягивание последней колонки
        self.history_table.horizontalHeader().setStretchLastSection(True)

        history_layout.addWidget(self.history_table)
        history_layout.addWidget(self.history_status)

        # Кнопки управления историей
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_clear_history)
        button_layout.addWidget(self.btn_export_history)
        button_layout.addStretch()

        history_layout.addLayout(button_layout)

    def setup_styles_and_background(self) -> None:
        """Настраивает стили и фон виджетов."""
        # Загружаем стиль из QSS файла
        stylesheet = load_stylesheet("main")

        # Пробуем загрузить фон
        bg_url = get_background_url("bg")
        if bg_url:
            # Добавляем фоновое изображение к стилю
            bg_style = f"\nQMainWindow {{\n    border-image: {bg_url} 0 0 0 0 stretch stretch;\n}}"
            stylesheet += bg_style

        self.setStyleSheet(stylesheet)

        # Устанавливаем objectName для CSS селекторов
        self.central_widget.setObjectName("central_widget")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.get_weather_btn.setObjectName("get_weather_btn")
        self.weather_output.setObjectName("weather_output")
        self.weather_output.setReadOnly(True)
        self.weather_output.setPlaceholderText(PLACEHOLDER_WEATHER)
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setVisible(False)

        # Настройки для истории
        self.history_group.setObjectName("history_group")
        self.history_table.setObjectName("history_table")
        self.history_status.setObjectName("history_status")
        self.history_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_clear_history.setObjectName("btn_clear_history")
        self.btn_export_history.setObjectName("btn_export_history")

    def setup_cursors(self) -> None:
        """Настраивает курсоры для виджетов."""
        self.get_weather_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.weather_output.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        self.btn_clear_history.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_export_history.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def setup_connections(self) -> None:
        """Настраивает соединения сигналов и слотов."""
        self.get_weather_btn.clicked.connect(self.on_get_weather_clicked)
        self.btn_clear_history.clicked.connect(self.on_clear_history_clicked)
        self.btn_export_history.clicked.connect(self.on_export_history_clicked)

    def init_weather_service(self) -> None:
        """Инициализирует сервис погоды."""
        try:
            self.weather_service = WeatherService()
            self.status_label.setText(STATUS_SERVICE_INIT)
        except Exception as e:
            self.status_label.setText(STATUS_SERVICE_ERROR)
            self.show_error(f"Ошибка инициализации: {str(e)}")
            self.get_weather_btn.setEnabled(False)

    def load_history(self) -> None:
        """Загружает историю запросов в таблицу."""
        try:
            records = self.history_manager.get_recent_history(limit=5)
            total_count = self.history_manager.get_total_count()

            if not records:
                self.history_status.setText(HISTORY_EMPTY)
                self.history_table.setRowCount(0)
                return

            self.history_table.setRowCount(len(records))

            for row, record in enumerate(records):
                # Время
                time_item = QTableWidgetItem(record["time"])
                time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.history_table.setItem(row, 0, time_item)

                # Температура (используем temperature_raw для получения числового значения)
                temp_item = QTableWidgetItem(record["temperature"])
                temp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Используем raw значение температуры для цветовой подсветки
                temp_value = record["temperature_raw"]
                if temp_value < 0:
                    # Можно добавить цвет, но просили без него
                    pass
                elif temp_value > 25:
                    pass

                self.history_table.setItem(row, 1, temp_item)

                # Описание погоды
                desc_item = QTableWidgetItem(record["description"])
                self.history_table.setItem(row, 2, desc_item)

            self.history_status.setText(f"📊 Показано: {len(records)} из {total_count} записей")

        except Exception as e:
            self.history_status.setText(f"❌ Ошибка загрузки истории: {str(e)}")
            print(f"Ошибка загрузки истории: {e}")

    def on_clear_history_clicked(self) -> None:
        """Обработчик нажатия кнопки очистки истории."""
        reply = QMessageBox.question(
            self,
            "Очистка истории",
            "Вы уверены, что хотите очистить всю историю запросов?\nЭто действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.history_manager.clear_history()
            if success:
                self.history_status.setText("✅ История очищена")
                self.load_history()  # Обновляем таблицу
                self.status_label.setText("✅ История очищена")
            else:
                self.show_error("Не удалось очистить историю")

    def on_export_history_clicked(self) -> None:
        """Обработчик нажатия кнопки экспорта истории."""
        try:
            from datetime import datetime

            # Генерируем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weather_history_{timestamp}.csv"

            # Экспортируем
            success, message = self.history_manager.export_to_csv(filename)

            if success:
                self.status_label.setText("✅ Данные экспортированы")
                QMessageBox.information(self, "Экспорт завершен", f"Данные успешно экспортированы в файл:\n{message}")
            else:
                self.status_label.setText(f"❌ {message}")
                self.show_error(message)

        except Exception as e:
            error_msg = f"Ошибка при экспорте: {str(e)}"
            self.status_label.setText(f"❌ {error_msg}")
            self.show_error(error_msg)

    def on_get_weather_clicked(self) -> None:
        """Обработчик нажатия кнопки получения погоды."""
        if not self.weather_service:
            self.show_error(ERROR_SERVICE_NOT_INIT)
            return

        # Блокируем кнопку и показываем прогресс
        self.get_weather_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText(STATUS_LOADING)

        # Меняем курсор на ожидание
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        # Используем QTimer для неблокирующего выполнения
        QTimer.singleShot(TIMER_DELAY_MS, self.fetch_weather)

    def fetch_weather(self) -> None:
        """Получает данные о погоде."""
        try:
            # Используем новый метод с уведомлениями
            weather_data, notifications = self.weather_service.get_weather_with_notifications()
            self.display_weather_with_notifications(weather_data, notifications)
            self.status_label.setText(STATUS_SUCCESS)

            # Обновляем историю после получения новых данных
            self.load_history()

        except Exception as e:
            self.show_error(f"Ошибка при получении погоды: {str(e)}")
            self.status_label.setText(STATUS_FETCH_ERROR)

        finally:
            # Восстанавливаем интерфейс
            self.get_weather_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            QApplication.restoreOverrideCursor()

    def display_weather_with_notifications(self, weather_data: WeatherData, notifications: list[str]) -> None:
        """Отображает данные о погоде и уведомления в интерфейсе."""
        from src.utils.pressure_converter import convert_pressure_to_mmhg

        pressure_mmhg = convert_pressure_to_mmhg(weather_data.pressure)

        # Форматируем данные о погоде
        weather_text = f"""🌤 ПОГОДА В ГОРОДЕ {weather_data.city.upper()}
══════════════════════════════════════════
🌡️ Температура:     {weather_data.temperature}°C
🤔 Ощущается как:   {weather_data.feels_like}°C
💧 Влажность:       {weather_data.humidity}%
📊 Давление:        {pressure_mmhg} мм рт. ст. ({weather_data.pressure} гПа)
☁️ Описание:        {weather_data.description}
💨 Скорость ветра:  {weather_data.wind_speed:.1f} м/с
══════════════════════════════════════════"""

        # Добавляем уведомления если они есть
        if notifications:
            # Убираем дубликаты уведомлений
            unique_notifications = []
            seen = set()
            for notification in notifications:
                if notification not in seen:
                    seen.add(notification)
                    unique_notifications.append(notification)

            weather_text += f"\n\n🔔 АКТИВНЫЕ РЕКОМЕНДАЦИИ ({len(unique_notifications)}):\n"
            weather_text += "─" * 50

            for i, notification in enumerate(unique_notifications, 1):
                weather_text += f"\n  {i}. {notification}"

        # Также выводим в консоль для отладки
        print("\n" + "=" * 50)
        print("Данные получены через GUI:")
        print(weather_text)
        print("=" * 50)

        self.weather_output.setText(weather_text)

    def show_error(self, message: str) -> None:
        """Показывает сообщение об ошибке."""
        QMessageBox.critical(self, ERROR_TITLE, message)
        self.weather_output.setText(f"❌ ОШИБКА\n{message}")


def main() -> None:
    """Запуск GUI приложения."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = WeatherWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
