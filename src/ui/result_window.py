import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import pyperclip
from ..config import AppConfig


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FoxTeX 识别结果")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(500, 450)
        self.cfg = AppConfig()

        layout = QVBoxLayout()

        # 1. 纯 WebView 界面
        self.webview = QWebEngineView()

        # 开启本地文件访问权限 (加载 index.html 需要)
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        # 禁用右键菜单
        self.webview.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        layout.addWidget(self.webview)

        # 2. 底部按钮区 (保留复制和关闭按钮)
        btn_layout = QHBoxLayout()
        self.btn_copy = QPushButton("复制 (Enter)")
        self.btn_copy.clicked.connect(self.copy_and_close)
        self.btn_close = QPushButton("关闭 (Esc)")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # ✅ 加载本地 HTML 文件
        index_path = self.cfg.TEMPLATES_DIR / "index.html"
        self.webview.setUrl(QUrl.fromLocalFile(str(index_path)))

    def set_content(self, latex_code):
        self.showNormal()
        self.activateWindow()

        # 等待页面加载完成后注入数据
        # 如果页面已经加载过，直接注入
        # 使用 json.dumps 自动处理转义字符，非常安全
        js_code = f"setContent({json.dumps(latex_code)});"
        self.webview.page().runJavaScript(js_code)

    def copy_and_close(self):
        # 异步获取 JS 里的内容
        def callback(result):
            if result:
                pyperclip.copy(result)
                print(f"✅ 已复制: {result}")
            self.hide()

        # 执行 JS 获取当前文本框的值
        self.webview.page().runJavaScript("getContent();", callback)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key.Key_Return and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.copy_and_close()