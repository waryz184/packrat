import os
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QCheckBox, QComboBox, QLineEdit,
    QFileDialog, QScrollArea, QWidget, QFrame,
    QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QSettings


class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setObjectName("SettingsDialog")
        self.setWindowTitle("settings")
        self.setModal(True)
        self.resize(720, 520)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet("QDialog#SettingsDialog { background: #0c0c0c; border: 1px solid #3a3a3a; }")

        self.settings = settings or QSettings("Packrat", "PackratApp")
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet("background: #111111; border-bottom: 1px solid #2a2a2a;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 16, 0)
        title = QLabel("› settings")
        title.setStyleSheet("color: #4ec9b0; font-size: 14px; font-weight: bold;")
        hl.addWidget(title)
        hl.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #2a2a2a;"
            "  border-radius: 4px; color: #888888; font-size: 11px; }"
            "QPushButton:hover { background: #f44747; color: #000000; border: 1px solid #f44747; }"
        )
        close_btn.clicked.connect(self.accept)
        hl.addWidget(close_btn)
        main.addWidget(header)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(160)
        sidebar.setStyleSheet("background: #0c0c0c; border-right: 1px solid #2a2a2a;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 10, 0, 10)
        sb_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self._nav_btns = []

        sections = [
            ("general",      self._make_general()),
            ("downloads",    self._make_downloads()),
            ("metadata",     self._make_metadata()),
            ("auth",         self._make_auth()),
            ("sponsorblock", self._make_sponsorblock()),
            ("advanced",     self._make_advanced()),
        ]
        for i, (name, widget) in enumerate(sections):
            btn = QPushButton(f"  {name}")
            btn.setObjectName("SettingsNav")
            btn.setCheckable(False)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("active", i == 0)
            self._style_nav(btn, i == 0)
            btn.clicked.connect(lambda _, idx=i, b=btn: self._switch(idx, b))
            sb_layout.addWidget(btn)
            self._nav_btns.append(btn)
            self.stack.addWidget(widget)

        sb_layout.addStretch()
        body.addWidget(sidebar)
        body.addWidget(self.stack, 1)
        main.addLayout(body, 1)

    def _style_nav(self, btn, active):
        if active:
            btn.setStyleSheet(
                "QPushButton { background: #1e1e1e; border: none; border-left: 2px solid #4ec9b0;"
                " color: #4ec9b0; padding: 10px; font-size: 12px; font-weight: bold; text-align: left; }"
            )
        else:
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; border-left: 2px solid transparent;"
                " color: #6a6a6a; padding: 10px; font-size: 12px; font-weight: bold; text-align: left; }"
                "QPushButton:hover { background: #111111; color: #a0a0a0; }"
            )

    def _switch(self, idx, btn):
        self.stack.setCurrentIndex(idx)
        for b in self._nav_btns:
            self._style_nav(b, b is btn)

    def _scroll_wrap(self, inner):
        sa = QScrollArea()
        sa.setWidget(inner)
        sa.setWidgetResizable(True)
        sa.setFrameShape(QFrame.Shape.NoFrame)
        sa.setStyleSheet("background: #0c0c0c;")
        return sa

    def _section_widget(self):
        w = QWidget()
        w.setStyleSheet("background: #0c0c0c;")
        ly = QVBoxLayout(w)
        ly.setContentsMargins(20, 16, 20, 16)
        ly.setSpacing(0)
        return w, ly

    def _row(self, layout, label, desc, widget):
        row = QFrame()
        row.setStyleSheet("border-bottom: 1px solid #1e1e1e;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 12, 0, 12)
        info = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #d4d4d4;")
        d = QLabel(desc)
        d.setStyleSheet("font-size: 11px; color: #6a6a6a;")
        info.addWidget(lbl)
        info.addWidget(d)
        rl.addLayout(info, 1)
        rl.addWidget(widget)
        layout.addWidget(row)

    def _toggle(self, checked=False):
        cb = QCheckBox()
        cb.setChecked(checked)
        cb.setStyleSheet(
            "QCheckBox::indicator { width: 18px; height: 18px; border-radius: 2px;"
            " background: #111111; border: 1px solid #3a3a3a; }"
            "QCheckBox::indicator:checked { background: #4ec9b0; border: 1px solid #4ec9b0; }"
        )
        return cb

    def _combo(self, items, selected=0):
        cb = QComboBox()
        cb.addItems(items)
        cb.setCurrentIndex(selected)
        cb.setStyleSheet(
            "QComboBox { background: #111111; border: 1px solid #2a2a2a;"
            " border-radius: 0px; color: #9cdcfe; padding: 4px 10px; min-width: 100px; font-size: 12px; }"
            "QComboBox::drop-down { border: none; }"
            "QComboBox QAbstractItemView { background: #1e1e1e; border: 1px solid #3a3a3a;"
            " color: #d4d4d4; selection-background-color: #264f78; outline: none; }"
        )
        return cb

    def _path_row(self, path="Not set"):
        w = QFrame()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(8)
        lbl = QLabel(path)
        lbl.setStyleSheet(
            "background: #111111; border: 1px solid #2a2a2a;"
            " color: #d4d4d4; font-size: 11px; padding: 4px 8px;"
        )
        btn = QPushButton("browse")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { background: #111111; border: 1px solid #2a2a2a;"
            " color: #888888; font-size: 11px; padding: 4px 10px; }"
            "QPushButton:hover { border: 1px solid #4ec9b0; color: #4ec9b0; }"
        )
        l.addWidget(lbl, 1)
        l.addWidget(btn)
        return w

    def _path_row_with_cb(self, label):
        w = QFrame()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(8)
        label.setStyleSheet(
            "background: #111111; border: 1px solid #2a2a2a;"
            " color: #ce9178; font-size: 11px; padding: 4px 8px;"
        )
        btn = QPushButton("browse")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { background: #111111; border: 1px solid #2a2a2a;"
            " color: #888888; font-size: 11px; padding: 4px 10px; }"
            "QPushButton:hover { border: 1px solid #4ec9b0; color: #4ec9b0; }"
        )
        btn.clicked.connect(self._browse_folder)
        l.addWidget(label, 1)
        l.addWidget(btn)
        return w

    def _make_general(self):
        w, ly = self._section_widget()
        self.dl_path_label = QLabel(
            self.settings.value("download_dir", os.path.expanduser("~/Downloads/Packrat"))
        )
        self._row(ly, "download location", "directory where media is saved", self._path_row_with_cb(self.dl_path_label))
        self.concurrent = self._combo(["1", "2", "3", "4", "5"], 1)
        self._row(ly, "concurrent downloads", "max parallel yt-dlp processes", self.concurrent)
        self.auto_start = self._toggle(True)
        self._row(ly, "auto-start", "resume queued downloads on launch", self.auto_start)
        ly.addStretch()
        return self._scroll_wrap(w)

    def _browse_folder(self):
        d = QFileDialog.getExistingDirectory(
            self, "select directory",
            self.settings.value("download_dir", os.path.expanduser("~/Downloads/Packrat"))
        )
        if d:
            self.dl_path_label.setText(d)
            self.settings.setValue("download_dir", d)

    def _make_downloads(self):
        w, ly = self._section_widget()
        self.def_format = self._combo(["best", "mp4", "mkv", "webm"])
        self._row(ly, "default container", "preferred video format", self.def_format)
        self.def_quality = self._combo(["best", "1080p", "720p", "480p", "360p"], 2)
        self._row(ly, "default quality", "preferred maximum vertical resolution", self.def_quality)
        self.subtitles = self._toggle(False)
        self._row(ly, "fetch subtitles", "auto-download available subs (*.srt, *.vtt)", self.subtitles)
        self.embed_thumb = self._toggle(True)
        self._row(ly, "embed thumbnail", "burn cover art into audio files", self.embed_thumb)
        ly.addStretch()
        return self._scroll_wrap(w)

    def _make_metadata(self):
        w, ly = self._section_widget()
        self.write_meta = self._toggle(True)
        self._row(ly, "write metadata", "embed ID3/MKV tags into output files", self.write_meta)
        self.write_json = self._toggle(False)
        self._row(ly, "write .info.json", "dump full yt-dlp metadata JSON", self.write_json)
        self.write_thumb = self._toggle(False)
        self._row(ly, "write thumbnail", "save cover art as separate image file", self.write_thumb)
        ly.addStretch()
        return self._scroll_wrap(w)

    def _make_auth(self):
        w, ly = self._section_widget()
        self._row(ly, "cookies.txt", "path to Netscape format cookies file", self._path_row("Not set"))
        self.browser_cookies = self._combo(["none", "chrome", "firefox", "safari", "brave"])
        self._row(ly, "browser integration", "extract auth state directly from browser", self.browser_cookies)
        ly.addStretch()
        return self._scroll_wrap(w)

    def _make_sponsorblock(self):
        w, ly = self._section_widget()
        self.sb_enabled = self._toggle(False)
        self._row(ly, "enable sponsorblock", "crowd-sourced sponsor skipping via API", self.sb_enabled)
        self.sb_intros = self._toggle(False)
        self._row(ly, "cut intros/outros", "automatically slice video intros and endcards", self.sb_intros)
        self.sb_selfpromo = self._toggle(False)
        self._row(ly, "cut self-promo", "remove subscribe/merch reminders", self.sb_selfpromo)
        ly.addStretch()
        return self._scroll_wrap(w)

    def _make_advanced(self):
        w, ly = self._section_widget()
        self.custom_args = QLineEdit()
        self.custom_args.setPlaceholderText("--force-ipv4 --geo-bypass ...")
        self.custom_args.setStyleSheet(
            "background: #111111; border: 1px solid #2a2a2a;"
            " color: #dcdcaa; font-size: 11px; padding: 6px 10px;"
        )
        self._row(ly, "custom flags", "raw yt-dlp arguments", self.custom_args)
        self.proxy_url = QLineEdit()
        self.proxy_url.setPlaceholderText("socks5://127.0.0.1:1080")
        self.proxy_url.setStyleSheet(self.custom_args.styleSheet())
        self._row(ly, "proxy string", "route all traffic through proxy", self.proxy_url)
        ly.addStretch()
        return self._scroll_wrap(w)

    def get_settings(self):
        return {
            "download_dir": self.dl_path_label.text(),
            "concurrent":   int(self.concurrent.currentText()),
            "subtitles":    self.subtitles.isChecked(),
            "embed_thumb":  self.embed_thumb.isChecked(),
            "custom_args":  self.custom_args.text(),
            "proxy_url":    self.proxy_url.text(),
        }

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton and e.position().y() < 40:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
