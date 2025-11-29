from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QBuffer, QIODevice, QPoint, QObject
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap


class SnipperOverlay(QWidget):
    """
    单个屏幕的遮罩层。
    有多少个屏幕，就实例化多少个这个类。
    """
    # 内部信号，通知管理器截图完成了
    finished = pyqtSignal(QPixmap)

    def __init__(self, screen):
        super().__init__()
        self.screen_handle = screen  # 持有它负责的那个屏幕对象的引用

        # 1. 设置窗口标志位 (无边框, 置顶, 工具窗口, 透明背景)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 2. 鼠标变成十字架
        self.setCursor(Qt.CursorShape.CrossCursor)

        # ✅ 关键：把自己精确地放到对应的屏幕上，并全屏
        self.setGeometry(screen.geometry())
        self.showFullScreen()

        # 状态变量
        self.start_pos = None
        self.current_pos = None
        self.is_selecting = False

        # 样式
        self.mask_color = QColor(0, 0, 0, 100)
        self.border_pen = QPen(QColor(0, 120, 215), 2)

    def showEvent(self, event):
        super().showEvent(event)
        # 每次显示时重置状态
        self.start_pos = None
        self.current_pos = None
        self.is_selecting = False
        self.update()

    def keyPressEvent(self, event):
        # 按 Esc 取消 (发送一个空图作为取消信号)
        if event.key() == Qt.Key.Key_Escape:
            self.finished.emit(QPixmap())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录在当前窗口内的局部坐标
            self.start_pos = event.pos()
            self.current_pos = event.pos()
            self.is_selecting = True
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.finished.emit(QPixmap())  # 右键取消

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False

            # 1. 获取选区矩形 (逻辑坐标)
            rect = QRect(self.start_pos, self.current_pos).normalized()

            # 防误触
            if rect.width() < 5 or rect.height() < 5:
                # 认为是取消
                self.finished.emit(QPixmap())
                return

            # 2. ✅ 核心修复：直接截取当前屏幕的指定逻辑区域
            # Qt会自动处理 DPI 换算，不需要我们手动乘 ratio 了
            # grabWindow 的参数是 (windowId, x, y, w, h)
            cropped_pixmap = self.screen_handle.grabWindow(
                0,
                rect.x(), rect.y(), rect.width(), rect.height()
            )

            # 发送截图结果给管理器
            self.finished.emit(cropped_pixmap)

    def paintEvent(self, event):
        """绘图逻辑 (和之前一样，挖空法)"""
        painter = QPainter(self)
        painter.setBrush(self.mask_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        if self.is_selecting and self.start_pos and self.current_pos:
            rect = QRect(self.start_pos, self.current_pos).normalized()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.setBrush(QColor(0, 0, 0, 0))
            painter.drawRect(rect)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(self.border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)


# ==========================================
# 管理器类 (对外提供接口)
# ==========================================
class SnipperManager(QObject):
    # 对外的信号：传出最终的 bytes
    captured = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        self.overlays = []  # 存放所有屏幕的遮罩窗口

    def start(self):
        """启动截图：给每个屏幕创建一个遮罩"""
        # 先清理旧的
        self.cleanup()

        screens = QApplication.screens()
        for screen in screens:
            overlay = SnipperOverlay(screen)
            # 连接每个遮罩的完成信号
            overlay.finished.connect(self._on_overlay_finished)
            overlay.show()
            # 尝试激活窗口 (有时候需要多试几次才能抢到焦点)
            overlay.activateWindow()
            overlay.raise_()
            self.overlays.append(overlay)

    def cleanup(self):
        """关闭并清理所有遮罩"""
        for overlay in self.overlays:
            overlay.close()
            overlay.deleteLater()
        self.overlays.clear()

    def _on_overlay_finished(self, pixmap):
        """当任何一个遮罩完成截图（或取消）时触发"""
        # 1. 不管成功失败，先清理所有屏幕的遮罩
        self.cleanup()

        # 2. 检查是否是空图 (取消操作)
        if pixmap.isNull() or pixmap.width() == 0:
            print("截图已取消")
            return

        # ✅ 【调试复活】保存图片看看对不对
        debug_path = "debug_final_capture.png"
        pixmap.save(debug_path)
        print(f"【调试】截图已保存到项目根目录: {debug_path}")

        # 3. 转 bytes 发射
        self._emit_bytes(pixmap)

    def _emit_bytes(self, pixmap):
        """序列化 QPixmap -> bytes"""
        ba = QBuffer()
        ba.open(QIODevice.OpenModeFlag.WriteOnly)
        success = pixmap.save(ba, "PNG")
        if success:
            self.captured.emit(bytes(ba.data()))
        else:
            print("❌ 图片序列化失败")
