import sys
import threading
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from src.config import AppConfig
from src.core.factory import create_engine  # ✅ 加这句
from src.ui.snipper import SnipperManager
import pyperclip
import keyboard  # ✅ 引入键盘库


# ✅ 定义一个信号桥，用于跨线程通讯
class HotkeyBridge(QObject):
    show_signal = pyqtSignal()


def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 1. 启动应用，且设置 quitOnLastWindowClosed 为 False
    # 这样即使所有窗口都 hide 了，程序也不会退出（常驻后台）
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    cfg = AppConfig()

    print("正在初始化引擎...")
    try:
        # ✅ 改回用工厂创建
        engine = create_engine("rapid", cfg)
        print("✅ 引擎就绪！请按 Alt+Q 截图，按 Esc 取消。")
    except Exception as e:
        print(f"❌ 引擎初始化失败: {e}")
        return

    # 2. 创建截图管理器 (原来是 Snipper)
    snipper_manager = SnipperManager()  # 改名了

    # 3. 创建热键桥梁
    bridge = HotkeyBridge()

    # 4. 定义业务逻辑
    def on_capture_finished(img_bytes):
        print("⚡ 收到截图，正在识别...")
        try:
            latex = engine.recognize(img_bytes)
            print(f"📝 识别结果: {latex}")
            if latex and "错误" not in latex:
                pyperclip.copy(latex)
                print("✅ 已复制到剪贴板")
        except Exception as e:
            print(f"❌ 流程异常: {e}")

    # 5. 信号连接
    # snipper.captured.connect(on_capture_finished)
    # 5. 信号连接
    # 连接管理器的信号
    snipper_manager.captured.connect(on_capture_finished)

    # 【关键】连接桥梁信号到 UI 显示槽
    # 当 bridge 发出 show_signal 时，主线程执行 snipper.show
    # bridge.show_signal.connect(snipper.show)
    # 【关键变化】桥梁连接到管理器的 start 方法
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

    # 7. 进入事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()