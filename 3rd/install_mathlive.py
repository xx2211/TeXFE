import os
import requests
import zipfile
from io import BytesIO
from pathlib import Path

# 1. 确定路径
current_dir = Path(__file__).parent.resolve()
web_dir = current_dir / "assets" / "web" # 放在 web 目录下
if not web_dir.exists():
    os.makedirs(web_dir)

# 2. MathLive 只有 npm 包，为了方便，我找了一个打包好的 CDN 链接下载
# 这里下载的是 mathlive.min.js 和 fonts
files = {
    "mathlive.min.js": "https://unpkg.com/mathlive@0.98.6/dist/mathlive.min.js",
}

print("正在下载 MathLive (可能需要一点时间)...")

for name, url in files.items():
    print(f"⬇️ 下载 {name}...")
    try:
        r = requests.get(url, timeout=60)
        with open(web_dir / name, "wb") as f:
            f.write(r.content)
        print("✅ 完成")
    except Exception as e:
        print(f"❌ 失败: {e}")

# 3. 字体是个大坑，MathLive 依赖 fonts 文件夹
# 我们简单一点，让它用 Base64 字体（新版 MathLive 支持）
# 或者为了稳妥，我们只下载核心 JS，字体让它回退到系统字体或联网
# 鉴于你是 MVP，我们先只用 JS，它会自动处理字体降级

print("-" * 30)
print("MathLive 核心已就绪。")