import os
import uuid
import datetime
from typing import Dict

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QScrollArea, QFrame,
    QStackedWidget, QTextEdit, QSizePolicy, QApplication,
    QProgressBar, QMenu
)
from PyQt6.QtCore import Qt, QPoint, QSettings
from PyQt6.QtGui import QFont, QMouseEvent, QColor, QPainter, QPainterPath, QRegion

from ui.style import STYLE
from ui.worker import DownloadWorker


class _RoundedWidget(QWidget):
    """Root widget that clips the window to a rounded rect shape."""

    def __init__(self, radius=12, bg_color="#0c0c0c", parent=None):
        super().__init__(parent)
        self._radius = radius
        self._bg = QColor(bg_color)

    def resizeEvent(self, event):
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self._radius, self._radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        super().resizeEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(self._bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(self.rect(), self._radius, self._radius)
        p.end()


class DLItem(QFrame):
    def __init__(self, item_id, url, fmt, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self._state = "active"

        self.setObjectName("DLItem")
        self.setProperty("state", "active")
        self.setFixedHeight(64)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        r1 = QHBoxLayout()
        r1.setSpacing(10)

        self.title_lbl = QLabel(f"[{item_id}] {url[:70]}{'…' if len(url) > 70 else ''}")
        self.title_lbl.setStyleSheet("color: #d4d4d4; font-size: 11px;")
        r1.addWidget(self.title_lbl, 1)

        self.fmt_lbl = QLabel(fmt.upper())
        self.fmt_lbl.setStyleSheet("color: #9cdcfe; font-size: 10px; min-width:40px;")
        r1.addWidget(self.fmt_lbl)

        self.pct_lbl = QLabel("0%")
        self.pct_lbl.setStyleSheet("color: #4ec9b0; font-size: 11px; min-width:36px;")
        r1.addWidget(self.pct_lbl)

        self.speed_lbl = QLabel("")
        self.speed_lbl.setStyleSheet("color: #555555; font-size: 10px; min-width:70px;")
        r1.addWidget(self.speed_lbl)

        self.status_lbl = QLabel("fetching…")
        self.status_lbl.setStyleSheet("color: #555555; font-size: 10px; min-width:60px;")
        r1.addWidget(self.status_lbl)

        self.btn_pause = self._mk_btn("pause")
        self.btn_cancel = self._mk_btn("cancel")
        r1.addWidget(self.btn_pause)
        r1.addWidget(self.btn_cancel)
        layout.addLayout(r1)

        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setValue(0)
        self.bar.setFixedHeight(2)
        self.bar.setTextVisible(False)
        layout.addWidget(self.bar)

    def _mk_btn(self, action):
        btn = QPushButton(action)
        btn.setObjectName("SmallBtn")
        btn.setFixedHeight(20)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def set_title(self, title):
        short = title[:80] + ("…" if len(title) > 80 else "")
        self.title_lbl.setText(f"[{self.item_id}] {short}")
        self.title_lbl.setToolTip(title)

    def set_progress(self, pct, speed, eta):
        self.bar.setValue(int(pct * 10))
        self.pct_lbl.setText(f"{pct:.1f}%")
        parts = [p for p in [speed, f"eta {eta}" if eta else ""] if p]
        self.speed_lbl.setText("  ".join(parts))
        self.status_lbl.setText("downloading")

    def set_done(self):
        self.bar.setValue(1000)
        self.bar.setStyleSheet("QProgressBar::chunk { background: #608b4e; }")
        self.pct_lbl.setText("100%")
        self.speed_lbl.setText("")
        self.status_lbl.setText("done")
        self.status_lbl.setStyleSheet("color: #608b4e; font-size: 10px;")
        self._set_state("done")
        self.btn_pause.setEnabled(False)
        self.btn_cancel.setEnabled(False)

    def set_error(self, msg):
        self.bar.setValue(0)
        self.bar.setStyleSheet("QProgressBar::chunk { background: #f44747; }")
        self.status_lbl.setText("error")
        self.status_lbl.setStyleSheet("color: #f44747; font-size: 10px;")
        self._set_state("error")
        self.btn_pause.setEnabled(False)

    def set_paused(self, paused):
        if paused:
            self.btn_pause.setText("resume")
            self.status_lbl.setText("paused")
            self.status_lbl.setStyleSheet("color: #dcdcaa; font-size: 10px;")
            self._set_state("paused")
        else:
            self.btn_pause.setText("pause")
            self.status_lbl.setText("downloading")
            self.status_lbl.setStyleSheet("color: #555555; font-size: 10px;")
            self._set_state("active")

    def _set_state(self, state):
        self._state = state
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)


class MainWindow(QMainWindow):
    def __init__(self, settings=None):
        super().__init__()
        self.setWindowTitle("packrat")
        self.resize(960, 680)
        self.setMinimumSize(720, 500)
        self.setStyleSheet(STYLE)

        self._drag_pos = QPoint()
        self._downloads: Dict[str, dict] = {}
        self._settings = settings or QSettings("Packrat", "PackratApp")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._build()

    def _build(self):
        root = _RoundedWidget(radius=12, bg_color="#0c0c0c")
        root.setObjectName("Root")
        self.setCentralWidget(root)

        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        vbox.addWidget(self._mk_top_bar())
        vbox.addWidget(self._hline())
        vbox.addWidget(self._mk_url_bar())
        vbox.addWidget(self._hline())
        vbox.addWidget(self._mk_tab_bar())
        vbox.addWidget(self._mk_stack(), 1)
        vbox.addWidget(self._hline())
        vbox.addWidget(self._mk_status_bar())

    def _mk_top_bar(self):
        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(38)
        l = QHBoxLayout(bar)
        l.setContentsMargins(12, 0, 12, 0)
        l.setSpacing(8)

        for color, cb in [("#ff5f56", self.close),
                          ("#febc2e", self.showMinimized),
                          ("#28c840", self._toggle_max)]:
            dot = QPushButton()
            dot.setFixedSize(12, 12)
            dot.setCursor(Qt.CursorShape.PointingHandCursor)
            dot.setStyleSheet(
                f"QPushButton {{ background: {color}; border-radius: 6px; border: none; }}"
                "QPushButton:hover { opacity: 0.8; }"
            )
            dot.clicked.connect(cb)
            l.addWidget(dot)

        l.addSpacing(10)
        title = QLabel("packrat")
        title.setStyleSheet("color: #3a3a3a; font-size: 12px; font-weight: bold; letter-spacing: 2px;")
        l.addWidget(title)
        l.addStretch()

        gear = QPushButton("settings")
        gear.setObjectName("SmallBtn")
        gear.setCursor(Qt.CursorShape.PointingHandCursor)
        gear.clicked.connect(self._open_settings)
        l.addWidget(gear)
        return bar

    def _toggle_max(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def _mk_url_bar(self):
        bar = QFrame()
        bar.setFixedHeight(46)
        bar.setStyleSheet("background: #0c0c0c;")
        l = QHBoxLayout(bar)
        l.setContentsMargins(12, 6, 12, 6)
        l.setSpacing(8)

        prompt = QLabel("›")
        prompt.setStyleSheet("color: #4ec9b0; font-size: 16px; font-weight: bold;")
        l.addWidget(prompt)

        self.url_input = QLineEdit()
        self.url_input.setObjectName("UrlInput")
        self.url_input.setPlaceholderText("paste url here and press enter…")
        self.url_input.setFixedHeight(30)
        self.url_input.returnPressed.connect(self._start)
        l.addWidget(self.url_input, 1)

        self.fmt_btn = QPushButton("best ▾")
        self.fmt_btn.setObjectName("FormatBtn")
        self.fmt_btn.setFixedHeight(30)
        self.fmt_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.fmt_menu = QMenu(self)
        self.fmt_menu.setObjectName("FormatMenu")
        for fmt in ["best", "1080p", "720p", "480p", "360p", "audio", "mp3", "aac", "flac"]:
            action = self.fmt_menu.addAction(fmt)
            action.triggered.connect(lambda checked, f=fmt: self.fmt_btn.setText(f"{f} ▾"))
            action.setData(fmt)

        self.fmt_btn.setMenu(self.fmt_menu)
        l.addWidget(self.fmt_btn)

        self.dl_btn = QPushButton("download")
        self.dl_btn.setObjectName("DownloadBtn")
        self.dl_btn.setFixedHeight(30)
        self.dl_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dl_btn.clicked.connect(self._start)
        l.addWidget(self.dl_btn)
        return bar

    def _mk_tab_bar(self):
        bar = QFrame()
        bar.setFixedHeight(36)
        bar.setStyleSheet("background: #0c0c0c;")
        l = QHBoxLayout(bar)
        l.setContentsMargins(12, 0, 12, 0)
        l.setSpacing(0)

        self._tab_btns = {}
        for name, label in [("queue", "queue"), ("logs", "logs")]:
            btn = QPushButton(label)
            btn.setObjectName("TabBtn")
            btn.setProperty("active", name == "queue")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._style_tab(btn, name == "queue")
            btn.clicked.connect(lambda _, n=name: self._switch_tab(n))
            self._tab_btns[name] = btn
            l.addWidget(btn)

        l.addStretch()

        self.clear_btn = QPushButton("clear done")
        self.clear_btn.setObjectName("SmallBtn")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self._clear_done)
        self.clear_btn.hide()
        l.addWidget(self.clear_btn)
        return bar

    def _style_tab(self, btn, active):
        if active:
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; border-bottom: 2px solid #4ec9b0;"
                " color: #4ec9b0; padding: 6px 14px; font-size: 12px; font-weight: bold; }"
            )
        else:
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; border-bottom: 2px solid transparent;"
                " color: #444444; padding: 6px 14px; font-size: 12px; font-weight: bold; }"
                "QPushButton:hover { color: #888888; }"
            )

    def _switch_tab(self, name):
        idx = {"queue": 0, "logs": 1}
        self._stack.setCurrentIndex(idx.get(name, 0))
        for k, b in self._tab_btns.items():
            self._style_tab(b, k == name)
        self.clear_btn.setVisible(name == "queue" and bool(self._downloads))

    def _mk_stack(self):
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: #0c0c0c;")
        self._stack.addWidget(self._mk_queue_page())
        self._stack.addWidget(self._mk_logs_page())
        return self._stack

    def _mk_queue_page(self):
        page = QWidget()
        page.setStyleSheet("background: #0c0c0c;")
        l = QVBoxLayout(page)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(0)

        self.empty_lbl = QLabel(
            "  no downloads yet\n\n"
            "  paste a url, choose a format, press download\n"
            "  supported: youtube · twitter · tiktok · soundcloud · vimeo · +1000 sites"
        )
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet("color: #2e2e2e; font-size: 12px; line-height: 2;")
        l.addWidget(self.empty_lbl, 1)

        self.scroll = QScrollArea()
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: #0c0c0c;")
        self.scroll.hide()

        self.queue_widget = QWidget()
        self.queue_widget.setStyleSheet("background: #0c0c0c;")
        self.queue_layout = QVBoxLayout(self.queue_widget)
        self.queue_layout.setContentsMargins(8, 8, 8, 8)
        self.queue_layout.setSpacing(4)
        self.queue_layout.addStretch()
        self.scroll.setWidget(self.queue_widget)
        l.addWidget(self.scroll, 1)
        return page

    def _mk_logs_page(self):
        self.logs = QTextEdit()
        self.logs.setObjectName("LogsOutput")
        self.logs.setReadOnly(True)
        self._log("sys", "packrat ready — yt-dlp v2026.02.21 · ffmpeg required for some formats")
        return self.logs

    def _mk_status_bar(self):
        bar = QFrame()
        bar.setObjectName("StatusBar")
        bar.setFixedHeight(24)
        l = QHBoxLayout(bar)
        l.setContentsMargins(12, 0, 12, 0)
        l.setSpacing(16)

        self.status_lbl = QLabel("idle")
        self.status_lbl.setObjectName("Dim")
        self.status_lbl.setStyleSheet("color: #3a3a3a; font-size: 11px;")
        l.addWidget(self.status_lbl)
        l.addStretch()

        ver = QLabel("packrat v1.0.0")
        ver.setStyleSheet("color: #2a2a2a; font-size: 11px;")
        l.addWidget(ver)
        return bar

    def _hline(self):
        f = QFrame()
        f.setObjectName("HLine")
        f.setFrameShape(QFrame.Shape.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet("background: #1e1e1e;")
        return f

    def _start(self):
        import sys

        def _safe_excepthook(exc_type, exc_val, exc_tb):
            import traceback
            self._log("err", f"Unhandled error: {''.join(traceback.format_exception(exc_type, exc_val, exc_tb))}")
        sys.excepthook = _safe_excepthook

        try:
            url = self.url_input.text().strip()
            if not url:
                return
            self.url_input.clear()

            fmt = self.fmt_btn.text().replace(" ▾", "").strip()
            item_id = str(uuid.uuid4())[:6]
            dl_dir = self._settings.value("download_dir", os.path.expanduser("~/Downloads/Packrat"))
            os.makedirs(dl_dir, exist_ok=True)

            item = DLItem(item_id, url, fmt)
            item.btn_pause.clicked.connect(lambda: self._toggle_pause(item_id))
            item.btn_cancel.clicked.connect(lambda: self._cancel(item_id))

            worker = DownloadWorker(url, fmt, dl_dir)
            worker.info_ready.connect(lambda t, u, th, w=item: w.set_title(t))
            worker.progress.connect(lambda p, s, e, w=item: w.set_progress(p, s, e))
            worker.finished.connect(lambda ok, msg, i=item_id: self._finished(i, ok, msg))
            worker.log_line.connect(self._log)

            self._downloads[item_id] = {"worker": worker, "widget": item, "done": False, "paused": False}

            self.queue_layout.insertWidget(self.queue_layout.count() - 1, item)
            self.empty_lbl.hide()
            self.scroll.show()
            self.clear_btn.show()

            worker.start()
            self._log("dl", f"[{item_id}] {url}  [{fmt}]")
            self._update_status()

        except Exception as e:
            self._log("err", f"Failed to start download: {e}")

    def _toggle_pause(self, item_id):
        d = self._downloads.get(item_id)
        if not d:
            return
        if d["paused"]:
            d["worker"].resume()
            d["paused"] = False
            d["widget"].set_paused(False)
            self._log("sys", f"[{item_id}] resumed")
        else:
            d["worker"].pause()
            d["paused"] = True
            d["widget"].set_paused(True)
            self._log("sys", f"[{item_id}] paused")

    def _cancel(self, item_id):
        d = self._downloads.get(item_id)
        if not d:
            return
        d["worker"].cancel()
        d["done"] = True
        d["widget"].set_error("cancelled")
        self._log("sys", f"[{item_id}] cancelled")
        self._update_status()

    def _finished(self, item_id, ok, msg):
        d = self._downloads.get(item_id)
        if not d:
            return
        d["done"] = True
        if ok:
            d["widget"].set_done()
            self._log("ok", f"[{item_id}] done")
        else:
            d["widget"].set_error(msg)
            self._log("err", f"[{item_id}] {msg}")
        self._update_status()

    def _clear_done(self):
        for item_id, d in list(self._downloads.items()):
            if d["done"]:
                w = d["widget"]
                self.queue_layout.removeWidget(w)
                w.deleteLater()
                del self._downloads[item_id]
        if not self._downloads:
            self.scroll.hide()
            self.empty_lbl.show()
            self.clear_btn.hide()
        self._update_status()

    def _update_status(self):
        active = sum(1 for d in self._downloads.values() if not d["done"])
        done = sum(1 for d in self._downloads.values() if d["done"])
        if active:
            self.status_lbl.setText(f"{active} active  ·  {done} done")
            self.status_lbl.setStyleSheet("color: #4ec9b0; font-size: 11px;")
        elif done:
            self.status_lbl.setText(f"{done} done")
            self.status_lbl.setStyleSheet("color: #608b4e; font-size: 11px;")
        else:
            self.status_lbl.setText("idle")
            self.status_lbl.setStyleSheet("color: #3a3a3a; font-size: 11px;")

    def _log(self, level, text):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        colors = {
            "sys":     "#3a6a5a",
            "dl":      "#4ec9b0",
            "ok":      "#608b4e",
            "err":     "#f44747",
            "warn":    "#dcdcaa",
            "info":    "#555555",
            "warning": "#dcdcaa",
            "error":   "#f44747",
            "success": "#608b4e",
        }
        color = colors.get(level, "#555555")
        line = (
            f'<span style="color:#2a2a2a;">{now}</span>'
            f'<span style="color:#1e1e1e;"> │ </span>'
            f'<span style="color:{color};">{text}</span>'
        )
        self.logs.append(line)
        sb = self.logs.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _open_settings(self):
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self, settings=self._settings)
        dlg.exec()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton and e.position().y() < 40:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
