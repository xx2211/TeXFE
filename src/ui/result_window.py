from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton,
                             QHBoxLayout, QApplication)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pyperclip
from ..config import AppConfig  # ✅ 引入配置


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FoxTeX 识别结果")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(500, 400)

        # ✅ 获取配置
        self.cfg = AppConfig()

        layout = QVBoxLayout()

        self.webview = QWebEngineView()

        self.webview.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.webview.setMinimumHeight(150)
        # 初始化
        self.webview.setHtml(self._get_html_template(""))
        layout.addWidget(self.webview)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        self.btn_copy = QPushButton("复制 (Enter)")
        self.btn_copy.clicked.connect(self.copy_and_close)
        self.btn_close = QPushButton("关闭 (Esc)")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.render_timer = QTimer()
        self.render_timer.setSingleShot(True)
        self.render_timer.interval = 300
        self.render_timer.timeout.connect(self.do_render)

        self.text_edit.textChanged.connect(self.on_text_changed)

    def _get_html_template(self, latex_code):
        print("-" * 40)
        print("🔍 [DEBUG] 开始追踪 LaTeX 字符串变化:")
        # 1. 打印原始输入
        print(f"1️⃣ 原始输入: {repr(latex_code)}")

        # 读取 JS 内容 (这一步没问题，不打印了)
        mathjax_path = self.cfg.MODEL_PATHS['mathjax']
        try:
            with open(mathjax_path, "r", encoding="utf-8") as f:
                mathjax_content = f.read()
        except Exception as e:
            return f"<h1>Error: {e}</h1>"


        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    overflow: hidden;
                    background-color: #ffffff;
                }}
                mjx-container {{ font-size: 2.5em !important; }}
            </style>

            <script>
            window.MathJax = {{
              tex: {{ inlineMath: [['$', '$']] }},
              svg: {{ fontCache: 'global' }},
              startup: {{ typeset: true }}
            }};
            </script>
            <script>
            {mathjax_content}
            </script>
        </head>
        <body>
            $${latex_code}$$
        </body>
        </html>
        """
        return html

    def set_content(self, latex_code):
        self.text_edit.blockSignals(True)
        self.text_edit.setText(latex_code)
        self.text_edit.blockSignals(False)
        self.do_render()
        self.showNormal()
        self.activateWindow()

    def on_text_changed(self):
        self.render_timer.start(300)

    def do_render(self):
        latex = self.text_edit.toPlainText().strip()
        if not latex:
            return

        html_content = self._get_html_template(latex)

        self.webview.setHtml(html_content)

    def copy_and_close(self):
        latex = self.text_edit.toPlainText()
        pyperclip.copy(latex)
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key.Key_Return and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.copy_and_close()