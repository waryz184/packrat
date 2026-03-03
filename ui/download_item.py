import os
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest


class DownloadItemWidget(QFrame):
    pause_requested  = pyqtSignal(str)
    resume_requested = pyqtSignal(str)
    cancel_requested = pyqtSignal(str)

    def __init__(self, item_id, url, fmt, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.url = url
        self.fmt = fmt
        self._paused = False
        self._nam = QNetworkAccessManager(self)

        self.setObjectName("DownloadItem")
        self.setFixedHeight(76)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(12)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(72, 46)
        self.thumb_label.setScaledContents(True)
        self.thumb_label.setStyleSheet("background: rgba(255,255,255,8); border-radius: 6px;")
        self._set_placeholder_thumb()
        root.addWidget(self.thumb_label)

        mid = QVBoxLayout()
        mid.setSpacing(5)
        mid.setContentsMargins(0, 0, 0, 0)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        self.title_lbl = QLabel("Fetching info…")
        self.title_lbl.setObjectName("CardTitle")
        self.title_lbl.setStyleSheet("font-size:13px; font-weight:500; color:rgba(255,255,255,220);")
        self.title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.badge = QLabel(self.fmt.upper())
        self.badge.setObjectName("BadgeLabel")
        self.badge.setFixedHeight(18)
        title_row.addWidget(self.title_lbl)
        title_row.addWidget(self.badge)
        mid.addLayout(title_row)

        prog_row = QHBoxLayout()
        prog_row.setSpacing(10)
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        prog_row.addWidget(self.progress)
        mid.addLayout(prog_row)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(12)
        self.pct_lbl = QLabel("0%")
        self.pct_lbl.setStyleSheet("font-size:11px; font-weight:600; color:rgba(255,255,255,200); font-family: monospace;")
        self.pct_lbl.setMinimumWidth(36)
        self.speed_lbl = QLabel("")
        self.speed_lbl.setObjectName("MetaLabel")
        self.speed_lbl.setStyleSheet("font-size:11px; color:rgba(255,255,255,80); font-family: monospace;")
        self.status_lbl = QLabel("Preparing…")
        self.status_lbl.setObjectName("MetaLabel")
        self.status_lbl.setStyleSheet("font-size:11px; color:rgba(255,255,255,80);")
        meta_row.addWidget(self.pct_lbl)
        meta_row.addWidget(self.speed_lbl)
        meta_row.addWidget(self.status_lbl)
        meta_row.addStretch()
        mid.addLayout(meta_row)

        root.addLayout(mid, 1)

        ctrl = QVBoxLayout()
        ctrl.setSpacing(4)
        ctrl.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.btn_pause = self._mk_ctrl_btn("⏸", "Pause")
        self.btn_pause.clicked.connect(self._on_pause)
        self.btn_cancel = self._mk_ctrl_btn("✕", "Cancel")
        self.btn_cancel.clicked.connect(self._on_cancel)
        ctrl.addWidget(self.btn_pause)
        ctrl.addWidget(self.btn_cancel)
        root.addLayout(ctrl)

    def _mk_ctrl_btn(self, text, tooltip):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(26, 26)
        btn.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,8); border: 1px solid rgba(255,255,255,18);"
            "  border-radius: 6px; color: rgba(255,255,255,100); font-size: 11px; }"
            "QPushButton:hover { background: rgba(255,255,255,16); color: white; }"
        )
        return btn

    def _on_pause(self):
        if self._paused:
            self._paused = False
            self.btn_pause.setText("⏸")
            self.status_lbl.setText("")
            self.resume_requested.emit(self.item_id)
        else:
            self._paused = True
            self.btn_pause.setText("▶")
            self.status_lbl.setText("Paused")
            self.pause_requested.emit(self.item_id)

    def _on_cancel(self):
        self.cancel_requested.emit(self.item_id)

    def set_info(self, title, uploader, thumb_url):
        display = title[:80] + ("…" if len(title) > 80 else "")
        self.title_lbl.setText(display)
        self.title_lbl.setToolTip(title)
        if uploader:
            self.status_lbl.setText(uploader)
        if thumb_url:
            self._load_thumb(thumb_url)

    def set_progress(self, pct, speed, eta):
        self.progress.setValue(int(pct * 10))
        self.pct_lbl.setText(f"{pct:.1f}%")
        parts = [p for p in [speed, (f"ETA {eta}" if eta else "")] if p]
        self.speed_lbl.setText("  ".join(parts))

    def set_done(self):
        self.progress.setValue(1000)
        self.pct_lbl.setText("100%")
        self.speed_lbl.setText("")
        self.status_lbl.setText("✓ Done")
        self.status_lbl.setStyleSheet("font-size:11px; color:#4ade80; font-weight:600;")
        self.btn_pause.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress.setStyleSheet("QProgressBar::chunk { background: #4ade80; border-radius: 2px; }")

    def set_error(self, msg):
        self.status_lbl.setText(f"✕ {msg[:60]}")
        self.status_lbl.setStyleSheet("font-size:11px; color:#f87171; font-weight:600;")
        self.btn_pause.setEnabled(False)
        self.progress.setStyleSheet("QProgressBar::chunk { background: #f87171; border-radius: 2px; }")

    def _set_placeholder_thumb(self):
        pix = QPixmap(72, 46)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(255, 255, 255, 15))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, 72, 46, 6, 6)
        p.setPen(QColor(255, 255, 255, 60))
        p.setFont(self.font())
        p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "▶")
        p.end()
        self.thumb_label.setPixmap(pix)

    def _load_thumb(self, url):
        req = QNetworkRequest(QUrl(url))
        reply = self._nam.get(req)
        reply.finished.connect(lambda: self._on_thumb_ready(reply))

    def _on_thumb_ready(self, reply):
        data = reply.readAll()
        if data:
            pix = QPixmap()
            pix.loadFromData(data)
            if not pix.isNull():
                self.thumb_label.setPixmap(
                    pix.scaled(72, 46, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
                )
        reply.deleteLater()
