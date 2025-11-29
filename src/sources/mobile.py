from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from src.sources.server import BridgeServer
from src.ui.qr_window import QRWindow
from src.ui.image_editor import ImageEditor


class MobileSource(QObject):
    # 对外唯一的信号：产出最终图片
    captured = pyqtSignal(bytes)

    def __init__(self, config):
        super().__init__()
        self.cfg = config

        # 1. 内部组件：服务器
        self.server = BridgeServer(self.cfg.TEMPLATES_DIR, port=8989)
        self.server.signals.image_received.connect(self._on_raw_image_received)

        # 2. 内部组件：编辑器
        self.editor = ImageEditor()
        self.editor.confirmed.connect(self._on_editor_confirmed)

        # 3. 内部状态：二维码窗口引用
        self.qr_window = None

    def start(self):
        """外部调用此方法，启动手机流程"""
        # 启动服务器
        url = self.server.start()

        # 如果编辑器开着，就别弹二维码了，直接置顶编辑器
        if self.editor.isVisible():
            self.editor.activateWindow()
            return

        # 弹出二维码
        if self.qr_window:
            self.qr_window.close()

        self.qr_window = QRWindow(url)
        self.qr_window.show()

    def _on_raw_image_received(self, raw_bytes):
        """内部逻辑：收到手机传来的原始图片"""
        print("📱 MobileSource: 收到原始图片，启动编辑器...")

        # 1. 关掉二维码
        if self.qr_window:
            self.qr_window.close()
            self.qr_window = None

        # 2. 打开编辑器让用户修图
        self.editor.set_image(raw_bytes)

    def _on_editor_confirmed(self, final_bytes):
        """内部逻辑：用户编辑完成"""
        print("✅ MobileSource: 图片编辑完成，对外发射信号")
        # 3. 发射最终信号
        self.captured.emit(final_bytes)