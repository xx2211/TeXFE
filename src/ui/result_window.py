import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import pyperclip
from ..config import AppConfig


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 标准窗口
        self.setWindowTitle("FoxTeX")
        self.resize(600, 400)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.cfg = AppConfig()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 0边距，让HTML填满

        self.webview = QWebEngineView()

        # 权限
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)

        # 禁用右键
        self.webview.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # 监听
        self.webview.titleChanged.connect(self.handle_js_command)
        self.webview.loadFinished.connect(self._on_loaded)

        layout.addWidget(self.webview)
        self.setLayout(layout)

        # 加载
        index_path = self.cfg.TEMPLATES_DIR / "index.html"
        self.webview.setUrl(QUrl.fromLocalFile(str(index_path)))

        self.page_ready = False

    def _on_loaded(self, ok):
        self.page_ready = ok

    def set_content(self, latex_code, mouse_pos=None):
        self.show()
        self.activateWindow()

        if mouse_pos:
            self.move(mouse_pos.x() + 20, mouse_pos.y() + 20)

        # 注入数据
        js = f"setLatex({json.dumps(latex_code)});"
        if self.page_ready:
            self.webview.page().runJavaScript(js)

    def handle_js_command(self, title):
        """处理来自 HTML 按钮的指令"""
        if title == "CMD:CLOSE":
            self.hide()

        elif title.startswith("CMD:COPY:"):
            try:
                # 格式 CMD:COPY:内容
                # 注意：内容里可能有冒号，所以 split 要限制次数
                content = title.split(":", 2)[2]
                pyperclip.copy(content)
                print("✅ 已复制")
                self.hide()
            except:
                pass