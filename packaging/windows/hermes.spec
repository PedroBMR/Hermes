# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

block_cipher = None


a = Analysis(
    [
        os.path.join(project_root, 'hermes', '__main__.py'),
        os.path.join(project_root, 'hermes', 'api.py'),
    ],
    pathex=[project_root],
    binaries=[],
    datas=collect_data_files('hermes'),
    hiddenimports=['PyQt5', 'requests', 'apscheduler'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts[0],
    [],
    exclude_binaries=True,
    name='hermes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

exe_api = EXE(
    pyz,
    a.scripts[1],
    [],
    exclude_binaries=True,
    name='hermes_api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    exe_api,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hermes',
)
