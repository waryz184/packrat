STYLE = """
* {
    font-family: "JetBrains Mono", "SF Mono", "Menlo", "Courier New", monospace;
    font-size: 12px;
    color: #d4d4d4;
    background: transparent;
    border: none;
    outline: none;
}

/* ── Root / Window ── */
QMainWindow, QWidget#Root {
    background: #0c0c0c;
}

/* ── Top bar ── */
QFrame#TopBar {
    background: #111111;
    border-bottom: 1px solid #2a2a2a;
}

/* ── URL Input ── */
QLineEdit#UrlInput {
    background: #0c0c0c;
    border: 1px solid #2a2a2a;
    color: #e8e8e8;
    padding: 0 10px;
    selection-background-color: #264f78;
    font-size: 12px;
}
QLineEdit#UrlInput:focus {
    border: 1px solid #4ec9b0;
}
QLineEdit#UrlInput::placeholder {
    color: #3c3c3c;
}

/* ── Format ComboBox ── */
QComboBox#FormatCombo {
    background: #111111;
    border: 1px solid #2a2a2a;
    color: #9cdcfe;
    padding: 5px 24px 5px 8px;
    font-size: 12px;
    min-width: 100px;
}
/* Format Button & Dropdown Menu */
QPushButton#FormatBtn {
    background: #000000;
    border: 1px solid #2a2a2a;
    color: #888888;
    padding: 0 10px;
    min-width: 80px;
    text-align: center;
}
QPushButton#FormatBtn:hover {
    border: 1px solid #4ec9b0;
    color: #4ec9b0;
}
QPushButton#FormatBtn::menu-indicator {
    image: none;
}

QMenu#FormatMenu {
    background: #000000;
    border: 1px solid #4ec9b0;
    padding: 4px;
}
QMenu#FormatMenu::item {
    padding: 6px 20px 6px 12px;
    color: #4ec9b0;
}
QMenu#FormatMenu::item:selected {
    background: #4ec9b0;
    color: #000000;
}

/* ── Buttons ── */
QPushButton#DownloadBtn {
    background: #1e1e1e;
    border: 1px solid #4ec9b0;
    color: #4ec9b0;
    padding: 0 16px;
    font-size: 12px;
    font-weight: bold;
    min-width: 80px;
}
QPushButton#DownloadBtn:hover {
    background: #4ec9b0;
    color: #000000;
}
QPushButton#DownloadBtn:pressed {
    background: #3aa68c;
    color: #000000;
}

QPushButton#SmallBtn {
    background: transparent;
    border: 1px solid #2a2a2a;
    color: #6a6a6a;
    padding: 4px 10px;
    font-size: 11px;
}
QPushButton#SmallBtn:hover {
    border-color: #4a4a4a;
    color: #a0a0a0;
}

QPushButton#TabBtn {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: #555555;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton#TabBtn:hover { color: #888888; }
QPushButton#TabBtn[active="true"] {
    color: #4ec9b0;
    border-bottom: 2px solid #4ec9b0;
}

/* ── Dividers ── */
QFrame#HLine {
    background: #2a2a2a;
    max-height: 1px;
    min-height: 1px;
}
QFrame#VLine {
    background: #2a2a2a;
    max-width: 1px;
    min-width: 1px;
}

/* ── Download Item ── */
QFrame#DLItem {
    background: #111111;
    border: 1px solid #1e1e1e;
    border-left: 2px solid #2a2a2a;
}
QFrame#DLItem[state="active"]   { border-left: 2px solid #4ec9b0; }
QFrame#DLItem[state="done"]     { border-left: 2px solid #608b4e; }
QFrame#DLItem[state="error"]    { border-left: 2px solid #f44747; }
QFrame#DLItem[state="paused"]   { border-left: 2px solid #dcdcaa; }

/* ── Progress Bar ── */
QProgressBar {
    background: #1e1e1e;
    border: none;
    height: 2px;
    text-align: center;
    font-size: 0px;
}
QProgressBar::chunk {
    background: #4ec9b0;
}

/* ── Logs ── */
QTextEdit#LogsOutput {
    background: #0c0c0c;
    border: none;
    color: #608b4e;
    font-size: 11px;
    padding: 8px 12px;
    selection-background-color: #264f78;
}

/* ── Status Bar ── */
QFrame#StatusBar {
    background: #111111;
    border-top: 1px solid #1e1e1e;
}

/* ── Scroll bars ── */
QScrollBar:vertical {
    background: #111111;
    width: 6px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #2a2a2a;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #3a3a3a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Labels ── */
QLabel { color: #d4d4d4; }
QLabel#Dim    { color: #444444; }
QLabel#Accent { color: #4ec9b0; }
QLabel#Warn   { color: #dcdcaa; }
QLabel#Error  { color: #f44747; }
QLabel#OK     { color: #608b4e; }

/* ── Misc ── */
QScrollArea { background: #0c0c0c; }
QMainWindow::separator { background: #2a2a2a; }
"""
