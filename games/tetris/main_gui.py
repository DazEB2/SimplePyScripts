#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import json
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QToolButton,
    QPushButton,
    QScrollArea,
)

from src.core.common import logger, ms_to_str
from src.gui.common import StatusGameEnum
from src.gui.board_widget import BoardWidget
from src.gui.piece_widget import PieceWidget


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = f"{ex_cls.__name__}: {ex}:\n"
    text += "".join(traceback.format_tb(tb))

    logger.error(text)
    QMessageBox.critical(None, "Error", text)
    sys.exit(1)


sys.excepthook = log_uncaught_exceptions


# SOURCE: https://github.com/gil9red/parse_jira_logged_time/blob/9a842ed071f317b7323b7b7775aa9f5195dbaf47/widgets/__init__.py#L218
def get_scroll_area(widget: QWidget) -> QScrollArea:
    scroll_area = QScrollArea()
    scroll_area.setFrameStyle(QScrollArea.NoFrame)
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(widget)

    return scroll_area


DIR: Path = Path(__file__).resolve().parent
FILE_HIGH_SCORES: Path = DIR / "high_scores.json"


@dataclass
class HighScore:
    date_added: datetime
    time: str
    score: int

    @classmethod
    def parse(cls, data: dict[str, Any]) -> "HighScore":
        return cls(
            date_added=datetime.fromisoformat(data["date_added"]),
            time=data["time"],
            score=data["score"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "date_added": self.date_added.isoformat(),
            "time": self.time,
            "score": self.score,
        }


class MainWindow(QWidget):
    TITLE: str = "Tetris"

    def __init__(self):
        super().__init__()

        self.high_scores: list[HighScore] = []

        self.high_scores_view = QLabel()

        self.next_piece_widget = PieceWidget()
        self.score_label = QLabel()
        self.playing_time_label = QLabel()

        self.board_widget = BoardWidget()
        self.board_widget.board.on_next_piece.connect(self.next_piece_widget.set_piece)
        self.board_widget.board.on_update_score.connect(self._update_states)
        self.board_widget.on_tick.connect(self._update_states)
        self.board_widget.on_finish.connect(self._on_finish)

        def _add_button(text: str, key: Qt.Key) -> QToolButton:
            button = QToolButton()
            button.setText(text)
            button.clicked.connect(lambda: self.board_widget.process_key(key))
            return button

        self.up_button = _add_button("🢁", Qt.Key_Up)
        self.left_button = _add_button("🢀", Qt.Key_Left)
        self.right_button = _add_button("🢂", Qt.Key_Right)
        self.down_button = _add_button("🢃", Qt.Key_Down)
        self.pause_resume_button = _add_button("Pause/Resume", Qt.Key_Space)

        control_layout = QGridLayout()
        control_layout.addWidget(self.up_button, 0, 1)
        control_layout.addWidget(self.left_button, 1, 0)
        control_layout.addWidget(self.right_button, 1, 2)
        control_layout.addWidget(self.down_button, 2, 1)
        control_layout.addWidget(self.pause_resume_button, 3, 0, 1, 4)

        self.start_button = QPushButton("START")
        self.start_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.start_button.clicked.connect(
            lambda: self.board_widget.process_key(Qt.Key_Return)
        )

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.next_piece_widget)
        right_layout.addWidget(self.score_label)
        right_layout.addWidget(self.playing_time_label)
        right_layout.addWidget(self.start_button)
        right_layout.addLayout(control_layout)
        right_layout.addWidget(
            QLabel(
                """
                <table>
                    <tr><td colspan="2">ENTER - Start</td></tr>
                    <tr><td colspan="2">SPACE - Pause/Resume</td></tr>
                    <tr><td>🢁 - Rotate</td><td>🢀 - Left</td></tr>
                    <tr><td>🢂 - Right</td><td>🢃 - Down</td></tr>
                </table>
                <p>Scores by rows:</p>
                <table>
                    <tr><td><b>1</b>: 100</td><td><b>2</b>: 300</td></tr>
                    <tr><td><b>3</b>: 700</td><td><b>4</b>: 1500</td></tr>
                </table>
                """
            )
        )
        right_layout.addWidget(self.high_scores_view)
        right_layout.addStretch()

        widget_right = QWidget()
        widget_right.setLayout(right_layout)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.board_widget, stretch=1)
        main_layout.addWidget(get_scroll_area(widget_right))

        for w in self.findChildren(QWidget):
            if isinstance(w, BoardWidget):
                continue

            w.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.load_high_scores()

        self._update_states()

    def _on_finish(self):
        self.high_scores.append(
            HighScore(
                date_added=datetime.now(),
                time=ms_to_str(self.board_widget.playing_time_ms),
                score=self.board_widget.board.score,
            )
        )

        self._fill_high_scores_view()
        self.save_high_scores()

        self._update_states()

    def get_top_high_scores(self, number: int = 5) -> list[HighScore]:
        # Сортировка по убыванию очков и возрастанию времени
        self.high_scores.sort(
            key=lambda obj: (obj.score, -(int(obj.time.replace(":", "")))),
            reverse=True,
        )
        if len(self.high_scores) > number:
            self.high_scores = self.high_scores[:number]
        return self.high_scores

    def _update_states(self):
        score: int = self.board_widget.board.score
        playing_time = ms_to_str(self.board_widget.playing_time_ms)

        title_parts = [self.TITLE]

        if self.board_widget.status != StatusGameEnum.INITED:
            title_parts.append(f"Score: {score}")
            title_parts.append(f"Time: {playing_time}")

        if self.board_widget.status == StatusGameEnum.PAUSED:
            title_parts.append("Paused")

        self.setWindowTitle(". ".join(title_parts))
        self.score_label.setText(f"Score: {score}")
        self.playing_time_label.setText(f"Time: {playing_time}")

        self.start_button.setEnabled(
            self.board_widget.status in [StatusGameEnum.INITED, StatusGameEnum.FINISHED]
        )

        is_started = self.board_widget.status == StatusGameEnum.STARTED
        self.up_button.setEnabled(is_started)
        self.left_button.setEnabled(is_started)
        self.right_button.setEnabled(is_started)
        self.down_button.setEnabled(is_started)

        self.pause_resume_button.setEnabled(
            is_started or self.board_widget.status == StatusGameEnum.PAUSED
        )

    def _fill_high_scores_view(self):
        lines = ["High scores (top 5):"]

        for i, high_score in enumerate(self.get_top_high_scores(), start=1):
            lines.append(
                f"<b>{i}.</b> {high_score.score} - {high_score.time}<br/>"
                f"&nbsp;&nbsp;&nbsp;&nbsp;{high_score.date_added:%d.%m.%Y %H:%M:%S}"
            )

        self.high_scores_view.setText("<br/>".join(lines))

    def save_high_scores(self):
        FILE_HIGH_SCORES.write_text(
            json.dumps(
                [high_score.to_dict() for high_score in self.high_scores],
                indent=4,
            ),
            encoding="utf-8",
        )

    def load_high_scores(self):
        if not FILE_HIGH_SCORES.exists():
            return

        self.high_scores = [
            HighScore.parse(data)
            for data in json.loads(FILE_HIGH_SCORES.read_text(encoding="utf-8"))
        ]

        self._fill_high_scores_view()

    def keyReleaseEvent(self, event: QKeyEvent):
        self.board_widget.process_key(event.key())
        self._update_states()


if __name__ == "__main__":
    app = QApplication([])

    mw = MainWindow()
    mw.show()

    # mw = QWidget()
    # main_layout = QHBoxLayout(mw)
    #
    # for cls in Piece.__subclasses__():
    #     piece_widget = PieceWidget()
    #     piece_widget.set_piece(cls(0, 0))
    #     main_layout.addWidget(piece_widget)
    #
    # mw.show()

    app.exec()
