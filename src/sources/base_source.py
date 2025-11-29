from PyQt6.QtCore import QObject, pyqtSignal

class BaseSource(QObject):
    # 统一信号：当源头获取到图片时，发射 bytes
    image_ready = pyqtSignal(bytes)

    def start(self):
        """启动该源（比如弹出截图框，或启动服务器）"""
        pass