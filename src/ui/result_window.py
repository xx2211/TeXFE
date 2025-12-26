import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout, QApplication
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import pyperclip
from ..config import AppConfig


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TeXFE")
        self.resize(600, 400)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.cfg = AppConfig()

        # ✅ 改用堆叠布局：可以在 "浏览器" 和 "Loading" 之间切换
        self.stack = QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)

        # --- 页面 1: 浏览器 (显示结果) ---
        self.webview = QWebEngineView()
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        self.webview.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # 信号
        self.webview.titleChanged.connect(self.handle_js_command)
        self.webview.loadFinished.connect(self._on_loaded)

        # 加载 HTML
        index_path = self.cfg.TEMPLATES_DIR / "index.html"
        self.webview.setUrl(QUrl.fromLocalFile(str(index_path)))

        # --- 页面 2: 原生 Loading (显示加载中) ---
        self.loading_label = QLabel(self)
        self.loading_label.setText("🤔 正在识别中...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                background-color: white;
                color: #555;
                font-family: 'Segoe UI', sans-serif;
                font-size: 24px;
            }
        """)

        # 把两个页面都加进去
        self.stack.addWidget(self.webview)  # Index 0
        self.stack.addWidget(self.loading_label)  # Index 1

        self.page_ready = False

    def _on_loaded(self, ok):
        self.page_ready = ok
        if ok:
            print("✅ [UI] 结果页面加载完毕")
        else:
            print("❌ [UI] 结果页面加载失败，请检查 templates/index.html 路径")

        # 1. 新增：根据参考点（鼠标位置），把窗口移动到那个屏幕的正中间
    def move_to_screen_center_at(self, ref_pos):
        # 获取参考点所在的屏幕
        screen = QApplication.screenAt(ref_pos)
        if not screen:
            screen = QApplication.primaryScreen()

        # 获取该屏幕的可用区域 (去掉任务栏)
        screen_geo = screen.availableGeometry()

        # 计算该屏幕的中心坐标
        x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
        y = screen_geo.y() + (screen_geo.height() - self.height()) // 2

        self.move(x, y)

    # 2. 修改：接收一个可选的位置参数，用来定位屏幕
    def show_loading(self, ref_pos=None):
        self.stack.setCurrentIndex(1)

        # 如果传了鼠标位置，就根据鼠标位置找屏幕，并居中
        if ref_pos:
            self.move_to_screen_center_at(ref_pos)

        self.show()
        self.activateWindow()
        self.repaint()

    def set_content(self, latex_code):
        """切换回浏览器页面并注入数据"""
        self.show()
        self.activateWindow()

        # 1. 切换回浏览器 (Index 0)
        self.stack.setCurrentIndex(0)

        # 2. 注入数据 (仅当页面加载好时)
        if self.page_ready:
            js = f"setLatex({json.dumps(latex_code)});"
            self.webview.page().runJavaScript(js)
        else:
            print("⚠️ [UI] 页面还没加载好，无法显示公式")

    def show_error(self, error_msg):
        """显示错误信息"""
        self.show()
        self.loading_label.setText(f"❌ 识别失败\n{error_msg}")
        self.stack.setCurrentIndex(1)  # 复用 Loading 页面显示错误

    def handle_js_command(self, title):
        if title.startswith("CMD:CLOSE"):
            self.hide()
        elif title.startswith("CMD:COPY:"):
            try:
                content = title.split(":", 2)[2]
                pyperclip.copy(content)
                self.hide()
            except:
                pass