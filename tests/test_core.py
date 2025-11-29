# test_core.py
import sys
import os

# 1. 强行把当前目录加入 Python 搜索路径
# 防止 Python 找不到 src 包 (这是新手最容易遇到的坑)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.config import AppConfig
from src.core.engines.rapid_engine import RapidEngine


def main():
    print("------------------------------------------------")
    print("🔥 开始点火测试...")

    # 2. 初始化配置
    try:
        cfg = AppConfig()
        print(f"✅ 配置加载成功，资源目录: {cfg.ASSETS_DIR}")
    except Exception as e:
        print(f"❌ 配置炸了: {e}")
        return

    # 3. 初始化引擎 (这里会加载模型，可能会花几秒)
    print("⏳ 正在加载 AI 引擎 (RapidEngine)...")
    try:
        engine = RapidEngine(cfg)
        print("✅ 引擎初始化成功！模型已加载。")
    except Exception as e:
        print(f"❌ 引擎炸了: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. 找张图测一下
    # 请你在根目录下放一张包含公式的图片，命名为 test.png
    # 如果没有，代码会报错
    img_path = "D:/test.png"
    if not os.path.exists(img_path):
        print(f"⚠️ 警告: 找不到 {img_path}，无法测试推理。")
        print("请截图一个数学公式，保存为 test.png 放在项目根目录，然后再运行此脚本。")
        return

    print(f"🖼️ 正在识别图片: {img_path} ...")
    try:
        # RapidEngine 支持直接传路径字符串
        result = engine.recognize(img_path)
        print("------------------------------------------------")
        print(f"🎉 识别结果:\n{result}")
        print("------------------------------------------------")
    except Exception as e:
        print(f"❌ 推理过程炸了: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()