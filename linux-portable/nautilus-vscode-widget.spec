# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../nautilus-vscode-widget.py'],
    pathex=[],
    binaries=[],
    datas=[('../icon.svg', '.')],
    hiddenimports=['gi', 'cairo', 'Xlib', 'Xlib.display', 'Xlib.protocol', 'Xlib.X', 'gi.repository.Gtk', 'gi.repository.Gdk', 'gi.repository.GLib', 'gi.repository.GdkPixbuf', 'gi.repository.GObject', 'gi.repository.Gio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='nautilus-vscode-widget',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../icon.svg'],
)
