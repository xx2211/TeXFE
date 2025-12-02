import ctypes
from ctypes import wintypes
from PyQt6.QtCore import QObject, pyqtSignal, QAbstractNativeEventFilter

# Windows API 常量
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008


class GlobalHotKey(QObject):
    """
    使用 Windows 原生 API (RegisterHotKey) 实现的全局热键。
    完全不使用 Hook，因此不会被 360 报毒。
    """
    # 定义信号：按下热键时触发，参数是热键ID
    activated = pyqtSignal(int)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.user32 = ctypes.windll.user32
        self.hotkey_map = {}
        self.counter = 0

        # 安装原生事件过滤器
        self.filter = WinEventFilter(self.hotkey_map)
        self.filter.hotkey_signal.connect(self._on_hotkey)
        self.app.installNativeEventFilter(self.filter)

    def register(self, hwnd, modifiers, key_code):
        """
        注册热键
        :param hwnd: 窗口句柄 (int)，可以用 window.winId() 获取
        :param modifiers: 修饰键 (MOD_ALT | MOD_CONTROL 等)
        :param key_code: 键码 (比如 ord('Q'))
        """
        self.counter += 1
        hotkey_id = self.counter

        # 调用 Windows API
        success = self.user32.RegisterHotKey(
            int(hwnd), hotkey_id, modifiers, key_code
        )

        if success:
            self.hotkey_map[hotkey_id] = hotkey_id
            print(f"✅ 热键注册成功 ID:{hotkey_id}")
            return hotkey_id
        else:
            print("❌ 热键注册失败，可能被占用")
            return None

    def _on_hotkey(self, hotkey_id):
        self.activated.emit(hotkey_id)

    def unregister_all(self, hwnd):
        for hid in self.hotkey_map:
            self.user32.UnregisterHotKey(int(hwnd), hid)
        self.hotkey_map.clear()


class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, hotkey_map):
        super().__init__()
        self.hotkey_map = hotkey_map
        # 为了能发射信号，这里借用一个 QObject 代理（因为 Filter 不是 QObject）
        self.signals = _SignalProxy()
        self.hotkey_signal = self.signals.activated

    def nativeEventFilter(self, eventType, message):
        if eventType == b"windows_generic_MSG" or eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY:
                hotkey_id = msg.wParam
                if hotkey_id in self.hotkey_map:
                    self.hotkey_signal.emit(hotkey_id)
                    # 返回 True 表示事件已处理，不再传递
                    # 但对于热键，通常不需要拦截后续
        return False, 0


class _SignalProxy(QObject):
    activated = pyqtSignal(int)