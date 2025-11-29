# 这样导入，Python 就知道 src 是个包了
from src.config import AppConfig
from src.core.engines.rapid_engine import RapidEngine


def test():
    # 1. 初始化配置
    cfg = AppConfig()

    # 2. 初始化引擎
    engine = RapidEngine(cfg)

    # 3. 测试一张图
    print("正在测试...")
    # 随便找张图的路径填进去，或者把这一行注释掉只测加载
    print(engine.recognize("D:/test.png"))
    print("模型加载成功！")


if __name__ == "__main__":
    test()