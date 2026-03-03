"""
py2app setup — builds Packrat.app
Run: python3 setup.py py2app
"""

from setuptools import setup

APP = ["main.py"]
DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,          # must be False for PyQt6
    "iconfile": "packrat.icns",       # app icon (converted below)
    "plist": {
        "CFBundleName":               "Packrat",
        "CFBundleDisplayName":        "Packrat",
        "CFBundleIdentifier":         "io.packrat.app",
        "CFBundleVersion":            "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHumanReadableCopyright":   "© 2026 Packrat",
        "NSHighResolutionCapable":    True,
        "LSMinimumSystemVersion":     "12.0",
        "NSRequiresAquaSystemAppearance": False,  # supports dark mode
    },
    "packages": [
        "PyQt6",
        "yt_dlp",
        "ui",
    ],
    "includes": [
        "PyQt6.QtWidgets",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtNetwork",
        "PyQt6.QtSvg",
    ],
    "excludes": [
        "tkinter",
        "wx",
        "gtk",
        "test",
        "unittest",
    ],
    "semi_standalone": False,
    "site_packages": True,
}

setup(
    name="Packrat",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
