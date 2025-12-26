# src/core/worker.py

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from src.core.factory import create_engine


class InferenceWorker(QObject):
    """
    后台推理工人类。
    它不仅负责推理，还负责在后台线程加载模型，防止启动卡顿。
    """
    # 信号定义
    initialized = pyqtSignal(bool, str)  # 模型加载完毕 (成功/失败, 消息)
    finished = pyqtSignal(str)  # 推理成功 (LaTeX结果)
    error = pyqtSignal(str)  # 推理出错 (错误信息)

    def __init__(self, config):
        super().__init__()
        self.cfg = config
        self.engine = None

    def init_engine(self):
        """
        这个方法将在子线程启动时自动调用
        """
        print("⚙️ [Worker] 正在后台加载模型...")
        try:
            # 耗时操作：加载 ONNX 模型
            self.engine = create_engine("rapid", self.cfg)
            print("✅ [Worker] 模型加载完毕")
            self.initialized.emit(True, "模型加载成功")
        except Exception as e:
            print(f"❌ [Worker] 模型加载失败: {e}")
            self.initialized.emit(False, str(e))

    def do_inference(self, img_bytes):
        """
        耗时操作：执行推理
        """
        if not self.engine:
            self.error.emit("引擎尚未初始化")
            return

        print("⚙️ [Worker] 开始推理...")
        try:
            # 这里的 recognize 是阻塞的，但因为我们在子线程，所以主界面不会卡
            latex = self.engine.recognize(img_bytes)

            # 简单的结果清洗
            if not latex:
                self.error.emit("未能识别出公式")
            elif "错误" in latex:
                self.error.emit(latex)
            else:
                self.finished.emit(latex)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(f"推理过程异常: {str(e)}")