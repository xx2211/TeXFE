# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import sys
import os

# ========================================================
# 1. 自动收集依赖资源
# ========================================================

# 收集 rapid_latex_ocr 可能缺少的隐式依赖
datas_rapid, binaries_rapid, hiddenimports_rapid = collect_all('rapid_latex_ocr')

# 收集 onnxruntime 的动态库（防止 Windows 下缺 DLL）
datas_ort, binaries_ort, hiddenimports_ort = collect_all('onnxruntime')

# ========================================================
# 2. 定义资源文件 (Add Data)
# ========================================================
# 格式: ('本地源路径', '打包后的内部路径')
# assets 文件夹在 main.py 同级目录
my_datas = [
    ('assets', 'assets'),
]

# 合并所有资源
all_datas = my_datas + datas_rapid + datas_ort
all_binaries = binaries_rapid + binaries_ort
all_hiddenimports = [
    'keyboard'
] + hiddenimports_rapid + hiddenimports_ort

# ========================================================
# 3. 打包配置
# ========================================================
block_cipher = None

a = Analysis(
    ['main.py'],  # 你的入口文件
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
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
    a.scripts,
    [],
    exclude_binaries=True,
    name='TeXFE',  # 生成的 exe 名字
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False=没有黑框, True=显示黑框(调试用)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 如果有图标文件，可以在这里指定，例如 icon='assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TeXFE',
)