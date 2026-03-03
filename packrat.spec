# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

yt_dlp_hidden = collect_submodules("yt_dlp")
yt_dlp_datas  = collect_data_files("yt_dlp")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=yt_dlp_datas + [
        ("ui/*.py", "ui"),
    ],
    hiddenimports=yt_dlp_hidden + [
        "PyQt6.QtWidgets",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtNetwork",
        "PyQt6.QtSvg",
        "ui.main_window",
        "ui.worker",
        "ui.download_item",
        "ui.settings_dialog",
        "ui.style",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "wx", "gtk", "test", "unittest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Packrat",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no terminal window
    icon="packrat.ico",     # see notes below
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Packrat",
)
