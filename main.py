import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QCursor  # 获取鼠标位置
from src.config import AppConfig
from src.core.factory import create_engine
from src.ui.snipper import SnipperManager
from src.ui.result_window import ResultWindow
from src.ui.tray import FoxTray  # ✅ 引入托盘
import keyboard

# ✅ 定义一个信号桥，用于跨线程通讯
class HotkeyBridge(QObject):
    show_signal = pyqtSignal()

def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关键：关了窗口不退程序

    cfg = AppConfig()

    try:
        engine = create_engine("rapid", cfg)
    except Exception as e:
        print(f"❌ 引擎初始化失败: {e}")
        return


    snipper_manager = SnipperManager()
    result_window = ResultWindow()  # ✅ 创建新的浮窗

    def start_capture():
        snipper_manager.start()

    bridge = HotkeyBridge()


    # ✅ 创建托盘图标，并绑定截图功能
    tray = FoxTray(on_capture=start_capture)

    def on_capture_finished(img_bytes):
        print("⚡ 识别中...")
        try:
            latex = engine.recognize(img_bytes)

            if latex and "错误" not in latex:
                # ✅ 获取当前鼠标位置，让浮窗出现在鼠标旁边
                # mouse_pos = QCursor.pos()
                result_window.set_content(latex)

        except Exception as e:
            print(f"❌ 异常: {e}")

    snipper_manager.captured.connect(on_capture_finished)

    # 5. 信号连接
    # 连接管理器的信号
    snipper_manager.captured.connect(on_capture_finished)

    # 【关键】连接桥梁信号到 UI 显示槽
    bridge.show_signal.connect(snipper_manager.start)

    # 6. 设置全局热键回调 (运行在子线程)
    def on_hotkey():
        # 千万别直接调 snipper.show()，会崩！
        # 要通过信号通知主线程
        bridge.show_signal.emit()

    # 注册热键 (Alt+Q)
    try:
        keyboard.add_hotkey(cfg.HOTKEY, on_hotkey)
    except ImportError:
        print("⚠️ 警告：keyboard 库需要 root/管理员权限才能在某些系统运行全局热键。")

    print(f"🚀 FoxTeX 已启动！按 {cfg.HOTKEY} 截图，托盘图标已就绪。")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()