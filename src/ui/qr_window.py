import qrcode
from io import BytesIO
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class QRWindow(QDialog):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("手机扫码拍照")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.resize(300, 350)

        layout = QVBoxLayout()

        # 提示文字
        lbl_hint = QLabel("请确保手机和电脑在同一 Wi-Fi 下")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_hint)

        # 生成二维码
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # PIL Image -> QPixmap
        im_data = img.convert("RGBA").tobytes("raw", "RGBA")
        qim = QImage(im_data, img.size[0], img.size[1], QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qim)

        # 显示图片
        lbl_img = QLabel()
        lbl_img.setPixmap(pixmap)
        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_img)

        lbl_url = QLabel(url)
        lbl_url.setStyleSheet("color: blue; text-decoration: underline;")
        lbl_url.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_url)

        self.setLayout(layout)