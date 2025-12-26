import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt6.QtGui import QCursor

from src.config import AppConfig
from src.core.worker import InferenceWorker
from src.ui.result_window import ResultWindow
from src.ui.tray import FoxTray
from src.sources.screen_source import SnipperManager
from src.sources.mobile_source import MobileSource
from src.ui.hotkey import GlobalHotKey, MOD_ALT
import pyperclip


# 信号桥
class HotkeyBridge(QObject):
    trigger_snipper = pyqtSignal()
    trigger_mobile = pyqtSignal()
    request_inference = pyqtSignal(bytes)


# ✅ 创建一个上下文类，专门用来持有这些对象，防止被垃圾回收
class AppContext:
    def __init__(self):
        self.cfg = AppConfig()
        self.bridge = HotkeyBridge()

        # UI
        self.result_window = ResultWindow()

        # Sources
        self.screen_source = SnipperManager()
        self.mobile_source = MobileSource(self.cfg)

        # Thread & Worker
        self.worker_thread = QThread()
        self.worker = InferenceWorker(self.cfg)
        self.worker.moveToThread(self.worker_thread)

        # Tray (要最后创建)
        self.tray = None
        self.hotkey_manager = None


def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # ✅ 实例化上下文，所有对象都在这里面活着
    ctx = AppContext()

    # --- 1. 线程连线 ---
    ctx.worker_thread.started.connect(ctx.worker.init_engine)
    ctx.worker_thread.start()  # 启动线程

    # --- 2. 业务连线 ---

    # 图片来源 -> 触发 Loading -> 触发推理
    def on_image_captured(img_bytes):
        print("⚡ [Main] 收到图片，显示 Loading 并请求后台...")
        # 立即显示原生 Loading
        ctx.result_window.show_loading(QCursor.pos())
        # 发送给后台
        ctx.bridge.request_inference.emit(img_bytes)

    ctx.screen_source.captured.connect(on_image_captured)
    ctx.mobile_source.captured.connect(on_image_captured)

    # 桥 -> 工人
    ctx.bridge.request_inference.connect(ctx.worker.do_inference)

    # 工人 -> UI
    def on_success(latex):
        print(f"✅ [Main] 识别成功: {latex[:15]}...")
        pyperclip.copy(latex)
        ctx.result_window.set_content(latex)

    def on_error(err_msg):
        print(f"❌ [Main] 识别出错: {err_msg}")
        ctx.result_window.show_error(err_msg)

    ctx.worker.finished.connect(on_success)
    ctx.worker.error.connect(on_error)

    # 打印初始化日志
    ctx.worker.initialized.connect(lambda ok, msg: print(f"🔧 [Worker] 初始化状态: {ok} | {msg}"))

    # --- 3. 触发源控制 ---
    ctx.bridge.trigger_snipper.connect(ctx.screen_source.start)
    ctx.bridge.trigger_mobile.connect(ctx.mobile_source.start)

    # --- 4. 托盘 ---
    ctx.tray = FoxTray(
        on_capture=lambda: ctx.bridge.trigger_snipper.emit(),
        on_mobile=lambda: ctx.bridge.trigger_mobile.emit()
    )

    # --- 5. 热键 ---
    try:
        ctx.hotkey_manager = GlobalHotKey(app)
        dummy = QWidget()
        hwnd = dummy.winId()
        ctx.hotkey_manager.register(hwnd, MOD_ALT, ord('Q'))
        ctx.hotkey_manager.register(hwnd, MOD_ALT, ord('M'))

        def handle_hotkey(hid):
            if hid == 1:
                ctx.bridge.trigger_snipper.emit()
            elif hid == 2:
                ctx.bridge.trigger_mobile.emit()

        ctx.hotkey_manager.activated.connect(handle_hotkey)
    except Exception as e:
        print(f"❌ 热键失败: {e}")


    if ctx.tray:
        ctx.tray.showMessage(
            '🚀 TeXFE 启动成功!',
            f'截图识别: {ctx.cfg.HOTKEY_SNIP}\n拍照识别: {ctx.cfg.HOTKEY_MOBILE}'
        )
    print("🚀 程序已启动，请尝试截图...")


    exit_code = app.exec()

    # 退出清理
    ctx.worker_thread.quit()
    ctx.worker_thread.wait()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()