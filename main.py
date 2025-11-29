import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QCursor

from src.config import AppConfig
from src.core.factory import create_engine
from src.ui.result_window import ResultWindow
from src.ui.tray import FoxTray

# 引入两个干净的 Source
from src.sources.screen_source import SnipperManager  # 这个本质上就是 ScreenSource
from src.sources.mobile_source import MobileSource  # ✅ 新写的封装类

import keyboard
import pyperclip


# 信号桥（防死锁）
class HotkeyBridge(QObject):
    trigger_snipper = pyqtSignal()
    trigger_mobile = pyqtSignal()


def main():
    # ... (HighDPI 设置不变) ...
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    cfg = AppConfig()

    # --- 1. 初始化核心 ---
    try:
        engine = create_engine("rapid", cfg)
    except Exception as e:
        print(f"❌ 引擎挂了: {e}")
        return

    result_window = ResultWindow()
    bridge = HotkeyBridge()

    # --- 2. 初始化输入源 (Sources) ---
    screen_source = SnipperManager()
    mobile_source = MobileSource(cfg)

    # --- 3. 统一的处理逻辑 (Sink) ---
    def process_image(img_bytes):
        print("⚡ 收到最终图片，开始识别...")
        try:
            latex = engine.recognize(img_bytes)
            if latex and "错误" not in latex:
                pyperclip.copy(latex)
                result_window.set_content(latex)
        except Exception as e:
            print(f"❌ 识别异常: {e}")

    # --- 4. 连线 (Wiring) ---

    # 无论是截图来的，还是手机修完图来的，都进同一个处理函数
    screen_source.captured.connect(process_image)
    mobile_source.captured.connect(process_image)

    # 信号桥 -> 启动源
    bridge.trigger_snipper.connect(screen_source.start)
    bridge.trigger_mobile.connect(mobile_source.start)

    # --- 5. 托盘与热键 ---

    # 托盘只负责发信号
    tray = FoxTray(
        on_capture=lambda: bridge.trigger_snipper.emit(),
        on_mobile=lambda: bridge.trigger_mobile.emit()
    )

    # 键盘监听 (后台线程)
    keyboard.add_hotkey(cfg.HOTKEY_SNIP, lambda: bridge.trigger_snipper.emit())
    keyboard.add_hotkey(cfg.HOTKEY_MOBILE, lambda: bridge.trigger_mobile.emit())

    print(f"🚀 TeXFE 启动成功")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()