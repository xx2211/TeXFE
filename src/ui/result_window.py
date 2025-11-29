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
        self.setWindowTitle("FoxTeX 结果")
        self.resize(600, 500)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.cfg = AppConfig()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.webview = QWebEngineView()

        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)

        # 监听 JS 消息
        self.webview.titleChanged.connect(self.handle_js_command)

        layout.addWidget(self.webview)
        self.setLayout(layout)

        # ✅ 【关键 1】初始化时就加载网页，且只加载这一次
        # 这样当你截图时，网页早就 ready 了，注入数据就不会失败
        editor_path = self.cfg.TEMPLATES_DIR / "editor.html"
        self.webview.setUrl(QUrl.fromLocalFile(str(editor_path)))

        # 标记网页是否加载完毕
        self.page_loaded = False
        self.webview.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self, ok):
        self.page_loaded = ok
        if ok:
            print("Web 编辑器加载完毕")

    def set_content(self, latex_code, mouse_pos=None):
        """外部调用：显示窗口并注入新公式"""
        self.show()
        self.activateWindow()

        if mouse_pos:
            # 简单的跟随鼠标逻辑（可选）
            # self.move(mouse_pos.x(), mouse_pos.y())
            pass

        # ✅ 【关键 2】不再 setUrl，而是直接注入 JS 清空并设置新内容
        # 使用 json.dumps 安全处理反斜杠
        js = f"setLatex({json.dumps(latex_code)});"

        if self.page_loaded:
            self.webview.page().runJavaScript(js)
        else:
            # 万一程序刚启动还没加载完网页（极低概率），先存着等加载完再设
            # 但因为是本地文件，通常很快
            pass

    def handle_js_command(self, title):
        """处理来自 HTML 的指令"""

        # ✅ 【关键 3】优先判断命令，逻辑拆分更清晰

        if title.startswith("CMD:CLOSE"):
            self.hide()
            return  # 处理完直接返回，不再往下走

        if title.startswith("CMD:COPY:"):
            # 格式: CMD:COPY:时间戳:内容
            # 我们需要把前面的前缀去掉
            # 找到第三个冒号的位置
            try:
                parts = title.split(":", 3)  # 分割成 ['CMD', 'COPY', '时间戳', '内容']
                if len(parts) >= 4:
                    content = parts[3]
                    pyperclip.copy(content)
                    print("✅ 已复制")
                    self.hide()
            except Exception as e:
                print(f"复制解析错误: {e}")
            return

        if title.startswith("LATEX:"):
            # 这里原本是用来同步 Python 里的 TextEdit 的
            # 但既然现在实现了 All-in-Web，Python 这边其实不需要存数据了
            # 除非你想做日志记录
            # content = title[6:]
            # print(f"实时编辑: {content}")
            pass