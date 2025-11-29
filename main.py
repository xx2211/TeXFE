import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QCursor

# 引入项目模块
from src.config import AppConfig
from src.core.factory import create_engine
from src.ui.snipper import SnipperManager
from src.ui.result_window import ResultWindow
from src.ui.tray import FoxTray
import keyboard
import pyperclip


# ✅✅✅ 【找回丢失的组件】信号桥
# 它的作用是把 keyboard 的后台线程信号，安全地转发给 Qt 的主线程
# 没有它，按快捷键 100% 卡死
class HotkeyBridge(QObject):
    trigger_signal = pyqtSignal()


def main():
    # 1. HighDPI 设置
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关键：关了窗口不退程序

    cfg = AppConfig()

    # 2. 初始化核心引擎
    print("正在初始化 AI 引擎...")
    try:
        engine = create_engine("rapid", cfg)
        print("✅ 引擎就绪！")
    except Exception as e:
        print(f"❌ 引擎初始化失败: {e}")
        return

    # 3. 初始化 UI 组件
    snipper_manager = SnipperManager()
    result_window = ResultWindow()

    # ✅ 初始化信号桥
    bridge = HotkeyBridge()

    # 4. 定义核心业务逻辑：开始截图
    def start_capture():
        snipper_manager.start()

    # 5. 定义核心业务逻辑：截图完成后的处理
    def on_capture_finished(img_bytes):
        print("⚡ 截图完成，正在识别...")
        try:
            # 调用 AI 识别
            latex_code = engine.recognize(img_bytes)

            if latex_code and "错误" not in latex_code:
                print(f"📝 识别成功: {latex_code}")

                # A. 写入剪贴板 (防止用户不想开窗口也能用)
                pyperclip.copy(latex_code)

                # B. 打开结果编辑窗口
                # 获取鼠标位置，尽量让窗口出现在鼠标附近（可选）
                # mouse_pos = QCursor.pos()
                # result_window.set_content(latex, mouse_pos)
                result_window.set_content(latex_code)

            else:
                print("⚠️ 识别结果为空或出错")

        except Exception as e:
            print(f"❌ 业务流程异常: {e}")

    # 6. 连接信号 (把各个模块焊死)

    # 截图管理器 -> 完成回调
    snipper_manager.captured.connect(on_capture_finished)

    # ✅ 信号桥 -> 开始截图
    # 只有通过这一步转发，才能保证 start_capture 在主线程执行
    bridge.trigger_signal.connect(start_capture)

    # 7. 设置托盘图标
    # 托盘点击 -> 这里的 start_capture 是安全的，因为托盘点击本身就是 Qt 事件
    tray = FoxTray(on_capture=start_capture)

    # 8. 注册全局热键 (运行在后台线程)
    def on_hotkey():
        # ❌ 绝对不能在这里直接调 start_capture()
        # ✅ 必须发射信号
        bridge.trigger_signal.emit()

    try:
        keyboard.add_hotkey(cfg.HOTKEY, on_hotkey)
        print(f"🚀 FoxTeX 已启动！快捷键: [{cfg.HOTKEY}]")
    except Exception as e:
        print(f"⚠️ 热键注册失败 (可能需要管理员权限): {e}")

    # 9. 启动事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()