# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
from PyInstaller.utils.hooks import collect_submodules


hiddenimports = [
	'gui',
	'core',
    'kivymd',
    'screeninfo',
    'Cryptodome.Cipher',
    'Cryptodome.Util',
    'Cryptodome.Random'
    'cryptography.hazmat.primitives',
    'bcrypt',
    'pyperclip',
    'reportlab.lib',
    'reportlab.pdfgen'
]

hiddenimports += collect_submodules('kivymd')
hiddenimports += collect_submodules('gui')
hiddenimports += collect_submodules('core')
hiddenimports += collect_submodules('screeninfo')
hiddenimports += collect_submodules('Cryptodome.Cipher')
hiddenimports += collect_submodules('Cryptodome.Util')
hiddenimports += collect_submodules('Cryptodome.Random')
hiddenimports += collect_submodules('cryptography.hazmat.primitives')
hiddenimports += collect_submodules('bcrypt')
hiddenimports += collect_submodules('pyperclip')
hiddenimports += collect_submodules('reportlab.lib')
hiddenimports += collect_submodules('reportlab.pdfgen')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[("assets\\images", "assets\\images")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'cv2',
        'numpy',
        'pygame'
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    'assets\\images\\splash_screen_image.jpg',
    binaries=a.binaries,
    datas=a.datas,
    splash_timeout=8,
    text_pos=None,
    text_size=13,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    Tree(".",
	     excludes=['*.pyc', '*.pyo', '*.spec', '*.log', '__pycache__', 'build', 'dist',
	               '*.git', '*.md', 'requirements.txt', 'test*', 'doc*', 'examples*',
	               '*.txt', '*.rst', 'LICENSE', 'README*', 'data']),
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
	*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='Lock-Shield',
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
    icon=['assets\\images\\profil_icon.ico']
)
