from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QCoreApplication

from src.ui.icon import get_fox_icon


class FoxTray(QSystemTrayIcon):
    def __init__(self, parent=None, on_capture=None):
        # 使用系统默认图标（或者你自己做一个 .ico 放 assets）
        # 这里为了省事，用了一个标准图标
        super().__init__(get_fox_icon(), parent)

        self.on_capture = on_capture

        # 设置提示文字
        self.setToolTip("TeXFE - 数学公式截图")

        # 创建右键菜单
        self.menu = QMenu()

        # 截图动作
        action_capture = QAction("截图 (Alt+Q)", self)
        action_capture.triggered.connect(self.trigger_capture)
        self.menu.addAction(action_capture)

        self.menu.addSeparator()

        # 退出动作
        action_quit = QAction("退出", self)
        action_quit.triggered.connect(QCoreApplication.instance().quit)
        self.menu.addAction(action_quit)

        self.setContextMenu(self.menu)

        # 左键点击托盘，直接截图
        self.activated.connect(self.on_activated)

        self.show()

    def trigger_capture(self):
        if self.on_capture:
            self.on_capture()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.trigger_capture()