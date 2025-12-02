from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QCoreApplication

from src.ui.icon import get_fox_icon


class FoxTray(QSystemTrayIcon):
    def __init__(self, parent=None, on_capture=None, on_mobile=None):
        super().__init__(get_fox_icon(), parent)

        self.on_capture = on_capture
        self.on_mobile = on_mobile

        # 设置提示文字
        self.setToolTip("TeXFE - 数学公式识别")

        # 创建右键菜单
        self.menu = QMenu()

        # 新增菜单项
        action_mobile = QAction("拍照识别 (Alt+M)", self)
        action_mobile.triggered.connect(self.trigger_mobile)
        self.menu.addAction(action_mobile)  # 插在最前面

        # 截图动作
        action_capture = QAction("截图识别 (Alt+Q)", self)
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

    def trigger_mobile(self):
        if self.on_mobile:
            self.on_mobile()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.trigger_capture()