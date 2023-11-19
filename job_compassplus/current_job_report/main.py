#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import datetime as dt
import sys
import time
import traceback

from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QToolButton,
    QPlainTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QWidgetAction,
    QMessageBox,
)
from PyQt5.QtGui import QColor, QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QRectF

from get_user_and_deviation_hours import (
    get_user_and_deviation_hours,
    get_quarter_user_and_deviation_hours,
    get_quarter_num,
    NotFoundReport,
)

# SOURCE: https://github.com/gil9red/SimplePyScripts/blob/405f08fcbf8b99ea64a58a73ee699cb1c0b5230e/qt__pyqt__pyside__pyqode/pyqt__QPainter__dynamic_draw_emoji_on_img/main.py#L44-L66
def draw_text_to_bottom_right(img: QPixmap, text: str, scale_text_from_img: float = 0.5):
    p = QPainter(img)

    factor = (img.width() * scale_text_from_img) / p.fontMetrics().width(text)
    if factor < 1 or factor > 1.25:
        f = p.font()
        point_size = f.pointSizeF() * factor
        if point_size > 0:
            f.setPointSizeF(point_size)
            p.setFont(f)

    # Bottom + right
    text_rect = p.fontMetrics().boundingRect(text)
    rect = QRectF(
        img.width() - text_rect.width(),
        img.height() - text_rect.height(),
        img.width(),
        img.height(),
    )

    p.drawText(rect, text)

    p = None  # NOTE: Иначе, почему-то будет ошибка


# Для отлова всех исключений, которые в слотах Qt могут "затеряться" и привести к тихому падению
def log_uncaught_exceptions(ex_cls, ex, tb):
    text = f"{ex_cls.__name__}: {ex}:\n"
    text += "".join(traceback.format_tb(tb))

    print("Error: ", text)
    QMessageBox.critical(None, "Error", text)
    sys.exit(1)


sys.excepthook = log_uncaught_exceptions


DIR: Path = Path(__file__).parent.resolve()
TRAY_ICON: str = str(DIR / "favicon.png")


class CheckJobReportThread(QThread):
    about_new_text = pyqtSignal(str)
    about_ok = pyqtSignal(bool)
    about_log = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.last_text = None
        self.ok = None

    def do_run(self):
        def _get_title(deviation_hours):
            ok = deviation_hours[0] != "-"
            return "Переработка" if ok else "Недоработка"

        today = dt.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
        self.about_log.emit(f"Check for {today}")

        text = ""
        deviation_hours = None
        quarter_deviation_hours = None

        try:
            name, deviation_hours = get_user_and_deviation_hours()
            ok = deviation_hours[0] != "-"
            text += name + "\n\n" + _get_title(deviation_hours) + " " + deviation_hours

        except NotFoundReport:
            text = "Отчет на сегодня еще не готов."
            ok = True

        try:
            _, quarter_deviation_hours = get_quarter_user_and_deviation_hours()
            if quarter_deviation_hours.count(":") == 1:
                quarter_deviation_hours += ":00"

            text += (
                "\n"
                + _get_title(quarter_deviation_hours)
                + " за квартал "
                + get_quarter_num()
                + " "
                + quarter_deviation_hours
            )

        except NotFoundReport:
            pass

        # Если часы за месяц не готовы, но часы за квартал есть
        if not deviation_hours and quarter_deviation_hours:
            ok = True

        if self.last_text != text:
            self.last_text = text

            text = f"Обновлено {today}\n{self.last_text}"
            self.about_new_text.emit(text)
            self.about_log.emit("    " + self.last_text + "\n")
        else:
            self.about_log.emit("    Ничего не изменилось\n")

        self.ok = ok
        self.about_ok.emit(self.ok)

    def run(self):
        while True:
            try:
                self.do_run()
                time.sleep(3600)

            except Exception as e:
                self.about_log.emit(f"Error: {e}")
                self.about_log.emit("Wait 60 secs")
                time.sleep(60)


class JobReportWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.info = QLabel()
        self.ok: bool = None

        self.quit_button = QToolButton()
        self.quit_button.setText("Quit")
        self.quit_button.setAutoRaise(True)
        self.quit_button.clicked.connect(QApplication.instance().quit)

        self.hide_button = QToolButton()
        self.hide_button.setText("Hide")
        self.hide_button.setAutoRaise(True)
        self.hide_button.clicked.connect(lambda x=None: self.parent().hide())

        self.log = QPlainTextEdit()
        self.log.setWindowTitle("Log")
        self.log.setMaximumBlockCount(500)
        self.log.hide()

        button_visible_log = QToolButton()
        button_visible_log.setText("+")
        button_visible_log.setToolTip("Show log")
        button_visible_log.setAutoRaise(True)
        button_visible_log.clicked.connect(self.log.show)

        button_refresh = QToolButton()
        button_refresh.setText("🔄")
        button_refresh.setToolTip("Refresh")
        button_refresh.setAutoRaise(True)

        layout = QVBoxLayout()
        layout.setSpacing(0)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.info)
        hlayout.addWidget(button_visible_log, alignment=Qt.AlignTop)
        layout.addLayout(hlayout)

        layout.addStretch()

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(button_refresh)
        layout_buttons.addStretch()
        layout_buttons.addWidget(self.quit_button)
        layout_buttons.addWidget(self.hide_button)

        layout.addLayout(layout_buttons)

        self.setLayout(layout)

        self.thread = CheckJobReportThread()
        self.thread.about_new_text.connect(self.info.setText)
        self.thread.about_ok.connect(self._set_ok)
        self.thread.about_log.connect(self._add_log)
        self.thread.start()

        button_refresh.clicked.connect(self.thread.do_run)

    def _set_ok(self, val: bool):
        self.ok = val
        self.update()

    def _add_log(self, val):
        print(val)
        self.log.appendPlainText(val)

    def paintEvent(self, event):
        super().paintEvent(event)

        color = QColor("#29AB87") if self.ok else QColor(255, 0, 0, 128)

        painter = QPainter(self)
        painter.setBrush(color)
        painter.setPen(color)
        painter.drawRect(self.rect())


# TODO: Нарисовать график
if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    tray = QSystemTrayIcon(QIcon(TRAY_ICON))

    def _on_about_log_or_ok(value: str | bool):
        if isinstance(value, str):
            text = "🔄"
        else:
            text = "✔️" if value else "❌"

        img = QPixmap(TRAY_ICON)
        draw_text_to_bottom_right(img, text, 0.8)
        tray.setIcon(QIcon(img))

    job_report_widget = JobReportWidget()
    job_report_widget.setFixedSize(230, 130)
    job_report_widget.thread.about_log.connect(_on_about_log_or_ok)
    job_report_widget.thread.about_ok.connect(_on_about_log_or_ok)

    job_report_widget_action = QWidgetAction(job_report_widget)
    job_report_widget_action.setDefaultWidget(job_report_widget)

    menu = QMenu()
    menu.addAction(job_report_widget_action)

    tray.setContextMenu(menu)
    tray.activated.connect(lambda x: menu.exec(tray.geometry().center()))

    tray.setToolTip("Compass Plus. Рапорт учета рабочего времени")
    tray.show()

    app.exec()
