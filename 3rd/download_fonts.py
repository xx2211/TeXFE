import os
import requests
from pathlib import Path

# 目标路径: assets/templates/fonts
target_dir = Path(__file__).parent / "assets" / "templates" / "fonts"
if not target_dir.exists():
    os.makedirs(target_dir)

# 字体列表 (根据你的报错日志整理的)
font_names = [
    "KaTeX_Main-Regular.woff2",
    "KaTeX_Main-BoldItalic.woff2",
    "KaTeX_Main-Bold.woff2",
    "KaTeX_Main-Italic.woff2",
    "KaTeX_Math-Italic.woff2",
    "KaTeX_Math-BoldItalic.woff2",
    "KaTeX_Caligraphic-Bold.woff2",
    "KaTeX_Caligraphic-Regular.woff2",
    "KaTeX_AMS-Regular.woff2",
    "KaTeX_Fraktur-Bold.woff2",
    "KaTeX_Fraktur-Regular.woff2",
    "KaTeX_SansSerif-Regular.woff2",
    "KaTeX_SansSerif-Italic.woff2",
    "KaTeX_SansSerif-Bold.woff2",
    "KaTeX_Script-Regular.woff2",
    "KaTeX_Typewriter-Regular.woff2",
    "KaTeX_Size1-Regular.woff2",
    "KaTeX_Size2-Regular.woff2",
    "KaTeX_Size3-Regular.woff2",
    "KaTeX_Size4-Regular.woff2",
]

base_url = "https://unpkg.com/mathlive@0.98.6/dist/fonts/"

print(f"正在下载字体到 {target_dir} ...")

for font in font_names:
    url = base_url + font
    save_path = target_dir / font

    # 如果文件已存在，跳过
    if save_path.exists() and save_path.stat().st_size > 0:
        print(f"✅ 已存在: {font}")
        continue

    print(f"⬇️ 下载: {font}")
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
        else:
            print(f"❌ 下载失败 (HTTP {r.status_code}): {font}")
    except Exception as e:
        print(f"❌ 网络错误: {e}")

print("字体下载完成！刷新页面试试。")