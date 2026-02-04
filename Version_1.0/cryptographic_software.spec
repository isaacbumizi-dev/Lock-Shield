# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[("E:\\Programmation\\Cryptographic_Software\\images", "images"), ("E:\\Programmation\\Cryptographic_Software\\fonts", "fonts")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    'E:\\Programmation\\Cryptographic_Software\\images\\splash_screen_image.jpg',
    binaries=a.binaries,
    datas=a.datas,
    splash_timeout=8,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,

)

exe = EXE(
    pyz,
	Tree("E:\\Programmation\\Cryptographic_Software"),
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
	*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='Cryptographic software',
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
    icon=['E:\\Programmation\\Cryptographic_Software\\images\\profil_icon.ico'],
)
