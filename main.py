#!/usr/bin/env python3
import sys
import os

os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_settings():
    base = get_base_dir()
    ini_path = os.path.join(base, "packrat.ini")
    # Use an ini file next to the exe so the app is truly portable (no registry, no AppData)
    return QSettings(ini_path, QSettings.Format.IniFormat)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Packrat")
    app.setOrganizationName("Packrat")
    app.setApplicationVersion("1.0.0")

    # prevent PyQt6 from hard-crashing on unhandled Python exceptions in slots
    def _excepthook(exc_type, exc_val, exc_tb):
        import traceback
        msg = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
        print(f"[packrat] {msg}", file=sys.stderr)
    sys.excepthook = _excepthook

    font = QFont("Inter", 13)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)

    window = MainWindow(settings=get_settings())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
