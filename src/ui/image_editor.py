from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QBuffer, QIODevice, QRect, QPoint, QSize
from PyQt6.QtGui import QPixmap, QTransform, QPainter, QColor, QPen


class CropLabel(QLabel):
    """
    一个支持鼠标画框的 Label
    """

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 存原始高清大图
        self.original_pixmap = None
        # 选框状态
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        self.selection_rect = QRect()

    def set_original_pixmap(self, pixmap):
        self.original_pixmap = pixmap
        self.reset_selection()
        self.refresh_display()

    def reset_selection(self):
        self.start_pos = None
        self.end_pos = None
        self.selection_rect = QRect()
        self.update()

    def refresh_display(self):
        """根据窗口大小，缩放显示图片"""
        if not self.original_pixmap: return

        # 限制显示大小，不要撑爆屏幕
        # 这里实际上利用了 Label 的 resizeEvent，但为了简单，我们让它跟随父容器
        # 实际上我们在 paintEvent 里画图，这里只做个占位
        self.update()

    def paintEvent(self, event):
        if not self.original_pixmap:
            super().paintEvent(event)
            return

        painter = QPainter(self)

        # 1. 计算缩放比例，保持长宽比显示
        # 目标尺寸（Label 的当前尺寸）
        target_size = self.size()
        # 按照 KeepAspectRatio 缩放
        scaled_pixmap = self.original_pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # 计算图片在 Label 里的偏移量（居中）
        x_offset = (target_size.width() - scaled_pixmap.width()) // 2
        y_offset = (target_size.height() - scaled_pixmap.height()) // 2

        # 绘制图片
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)

        # 2. 绘制选框
        if not self.selection_rect.isEmpty():
            painter.setPen(QPen(QColor(0, 120, 215), 2))  # 蓝色边框
            painter.setBrush(QColor(0, 120, 215, 50))  # 半透明填充
            painter.drawRect(self.selection_rect)

        # 存一下当前的缩放参数，供裁剪计算用
        self._current_scale_info = {
            'ratio': self.original_pixmap.width() / scaled_pixmap.width(),
            'x_offset': x_offset,
            'y_offset': y_offset,
            'scaled_w': scaled_pixmap.width(),
            'scaled_h': scaled_pixmap.height()
        }

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = True
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_pos = event.pos()
            # 限制选框在 Label 范围内
            self.selection_rect = QRect(self.start_pos, self.end_pos).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = False

    def get_cropped_image(self):
        """核心逻辑：把屏幕上的选框，映射回原始高清大图"""
        if not self.original_pixmap: return None

        # 如果没有选框，返回原图
        if self.selection_rect.isEmpty() or self.selection_rect.width() < 10:
            return self.original_pixmap

        info = self._current_scale_info
        ratio = info['ratio']

        # 1. 减去偏移量 (把 Label 坐标 转为 图片显示区域坐标)
        x = self.selection_rect.x() - info['x_offset']
        y = self.selection_rect.y() - info['y_offset']
        w = self.selection_rect.width()
        h = self.selection_rect.height()

        # 2. 乘上缩放比例 (把 显示坐标 转为 原始图片坐标)
        real_x = int(x * ratio)
        real_y = int(y * ratio)
        real_w = int(w * ratio)
        real_h = int(h * ratio)

        # 3. 边界检查
        real_rect = QRect(real_x, real_y, real_w, real_h)
        # 和原图取交集，防止截出去
        img_rect = self.original_pixmap.rect()
        final_rect = real_rect.intersected(img_rect)

        return self.original_pixmap.copy(final_rect)


class ImageEditor(QDialog):
    confirmed = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片处理 (旋转/裁剪) - TeXFE")
        self.resize(800, 600)  # 窗口大一点
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        # 1. 顶部提示
        lbl_hint = QLabel("💡 提示：按住鼠标左键框选裁剪区域")
        lbl_hint.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(lbl_hint)

        # 2. 自定义图片控件
        self.image_label = CropLabel()
        self.image_label.setStyleSheet("background-color: #333;")
        # 让 Label 可以收缩，这一步很关键，否则大图会撑大窗口
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        layout.addWidget(self.image_label, 1)  # 权重1，占满空间

        # 3. 工具栏
        btn_layout = QHBoxLayout()

        btn_rotate = QPushButton("↺ 旋转 90°")
        btn_rotate.clicked.connect(self.rotate)

        btn_reset = QPushButton("重置")
        btn_reset.clicked.connect(self.reset_view)

        btn_cancel = QPushButton("丢弃")
        btn_cancel.clicked.connect(self.close)

        btn_ok = QPushButton("⚡ 确认并识别 (Enter)")
        btn_ok.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 8px 20px;")
        btn_ok.clicked.connect(self.on_confirm)

        btn_layout.addWidget(btn_rotate)
        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def set_image(self, img_bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(img_bytes)
        self.image_label.set_original_pixmap(pixmap)
        self.show()
        self.activateWindow()

    def rotate(self):
        if not self.image_label.original_pixmap: return
        transform = QTransform().rotate(-90)
        new_pix = self.image_label.original_pixmap.transformed(transform)
        self.image_label.set_original_pixmap(new_pix)

    def reset_view(self):
        self.image_label.reset_selection()

    def on_confirm(self):
        # 获取最终处理过的图片（裁剪后）
        final_pixmap = self.image_label.get_cropped_image()
        if not final_pixmap: return

        ba = QBuffer()
        ba.open(QIODevice.OpenModeFlag.WriteOnly)
        final_pixmap.save(ba, "PNG")

        # 关闭窗口，发出信号
        self.confirmed.emit(ba.data().data())
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.on_confirm()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()