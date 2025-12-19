"""Главное окно приложения."""

import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.data_parser import WeatherData
from src.core.weather_service import WeatherService
from src.gui.constants import (
    BTN_GET_WEATHER,
    ERROR_SERVICE_NOT_INIT,
    ERROR_TITLE,
    MAIN_TITLE,
    PLACEHOLDER_WEATHER,
    STATUS_FETCH_ERROR,
    STATUS_LOADING,
    STATUS_READY,
    STATUS_SERVICE_ERROR,
    STATUS_SERVICE_INIT,
    STATUS_SUCCESS,
    TIMER_DELAY_MS,
    WEATHER_TEMPLATE,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_X,
    WINDOW_Y,
)
from src.gui.resource_manager import get_background_url, load_stylesheet


class WeatherWindow(QMainWindow):
    """Главное окно приложения погоды."""

    def __init__(self):
        super().__init__()
        self.weather_service: WeatherService | None = None

        # Виджеты
        self.central_widget: QWidget | None = None
        self.title_label: QLabel | None = None
        self.get_weather_btn: QPushButton | None = None
        self.progress_bar: QProgressBar | None = None
        self.weather_output: QTextEdit | None = None
        self.status_label: QLabel | None = None

        self.init_ui()
        self.init_weather_service()

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

    def setup_layout(self) -> None:
        """Настраивает компоновку виджетов."""
        layout = QVBoxLayout(self.central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        layout.addWidget(self.title_label)
        layout.addWidget(self.get_weather_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.weather_output)
        layout.addWidget(self.status_label)

        self.setCentralWidget(self.central_widget)

    def setup_styles_and_background(self) -> None:
        """Настраивает стили и фон виджетов."""
        # Загружаем основной стиль
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

    def setup_cursors(self) -> None:
        """Настраивает курсоры для виджетов."""
        self.get_weather_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.weather_output.setCursor(QCursor(Qt.CursorShape.IBeamCursor))

    def setup_connections(self) -> None:
        """Настраивает соединения сигналов и слотов."""
        self.get_weather_btn.clicked.connect(self.on_get_weather_clicked)  # type: ignore

    def init_weather_service(self) -> None:
        """Инициализирует сервис погоды."""
        try:
            self.weather_service = WeatherService()
            self.status_label.setText(STATUS_SERVICE_INIT)
        except Exception as e:
            self.status_label.setText(STATUS_SERVICE_ERROR)
            self.show_error(f"Ошибка инициализации: {str(e)}")
            self.get_weather_btn.setEnabled(False)

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

    def display_weather_with_notifications(self, weather_data: WeatherData, notifications: list[str]) -> None:
        """Отображает данные о погоде и уведомления в интерфейсе."""
        from src.gui.constants import WEATHER_TEMPLATE
        from src.utils.pressure_converter import convert_pressure_to_mmhg

        pressure_mmhg = convert_pressure_to_mmhg(weather_data.pressure)

        # Основные данные о погоде с использованием константы
        weather_text = WEATHER_TEMPLATE.format(
            city=weather_data.city.upper(),
            temperature=weather_data.temperature,
            feels_like=weather_data.feels_like,
            humidity=weather_data.humidity,
            pressure_mmhg=pressure_mmhg,
            pressure_hpa=weather_data.pressure,
            description=weather_data.description,
            wind_speed=weather_data.wind_speed,
        )

        # Добавляем уведомления если они есть
        if notifications:
            # Убираем дубликаты уведомлений (если таковые есть)
            unique_notifications = []
            seen = set()
            for notification in notifications:
                if notification not in seen:
                    seen.add(notification)
                    unique_notifications.append(notification)

            weather_text += f"\n\n🔔 АКТИВНЫЕ РЕКОМЕНДАЦИИ ({len(unique_notifications)}):\n"
            weather_text += "─" * 50  # Другой символ для разделителя

            for i, notification in enumerate(unique_notifications, 1):
                weather_text += f"\n  {i}. {notification}"

        # Также выводим в консоль для отладки
        print("\n" + "=" * 50)
        print("Данные получены через GUI:")
        print(weather_text)
        print("=" * 50)

        self.weather_output.setText(weather_text)

    def fetch_weather(self) -> None:
        """Получает данные о погоде."""
        try:
            # Используем новый метод с уведомлениями
            weather_data, notifications = self.weather_service.get_weather_with_notifications()
            self.display_weather_with_notifications(weather_data, notifications)
            self.status_label.setText(STATUS_SUCCESS)

        except Exception as e:
            self.show_error(f"Ошибка при получении погоды: {str(e)}")
            self.status_label.setText(STATUS_FETCH_ERROR)

        finally:
            # Восстанавливаем интерфейс
            self.get_weather_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            QApplication.restoreOverrideCursor()

    def display_weather(self, weather_data: WeatherData) -> None:
        """Отображает данные о погоде в интерфейсе."""
        from src.utils.pressure_converter import convert_pressure_to_mmhg

        pressure_mmhg = convert_pressure_to_mmhg(weather_data.pressure)

        weather_text = WEATHER_TEMPLATE.format(
            city=weather_data.city.upper(),
            temperature=weather_data.temperature,
            feels_like=weather_data.feels_like,
            humidity=weather_data.humidity,
            pressure_mmhg=pressure_mmhg,
            pressure_hpa=weather_data.pressure,
            description=weather_data.description,
            wind_speed=weather_data.wind_speed,
        )

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
