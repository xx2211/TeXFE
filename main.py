import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QObject, pyqtSignal

from src.config import AppConfig
from src.core.factory import create_engine
from src.ui.result_window import ResultWindow
from src.ui.tray import FoxTray

# 引入两个干净的 Source
from src.sources.screen_source import SnipperManager
from src.sources.mobile_source import MobileSource

from PyQt6.QtGui import QKeySequence
from src.ui.hotkey import GlobalHotKey, MOD_ALT

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

    # 热键注册（添加错误处理）
    try:
        hotkey_manger = GlobalHotKey(app)
        dummy_window = QWidget()  # 创建一个空窗口
        hwnd = dummy_window.winId()  # 用它的 ID
        hotkey_manger.register(hwnd, MOD_ALT, ord('Q'))
        hotkey_manger.register(hwnd, MOD_ALT, ord('M'))
        def handle_hotkey(hid):
            if hid == 1:
                bridge.trigger_snipper.emit()
            elif hid == 2:
                bridge.trigger_mobile.emit()
        hotkey_manger.activated.connect(handle_hotkey)
    except Exception as e:
        print(f"❌ 热键注册失败: {e}")
        # 可以显示系统通知
        tray.showMessage("热键注册失败", "请检查热键是否被其他程序占用")

    tray.showMessage('🚀 TeXFE 启动成功!', f'截图识别: {cfg.HOTKEY_SNIP}\n拍照识别: {cfg.HOTKEY_MOBILE}')
    print('🚀 TeXFE 启动成功!', f'截图识别: {cfg.HOTKEY_SNIP} 拍照识别: {cfg.HOTKEY_MOBILE}')

    sys.exit(app.exec())


if __name__ == "__main__":
    main()