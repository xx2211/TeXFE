from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QByteArray
import base64

# 一只极简的狐狸头 SVG (Base64编码)
FOX_SVG = """
PHN2ZyB2aWV3Qm94PSIwIDAgNjQgNjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2
ZyI+PHBhdGggZD0iTTMyIDJDNCAyIDIgMTQgMiAxNGwxNCAxMkw4IDU4bDcuNSA0TDMyIDQ2bD-
E2LjUgMTZMNCA1OGwtOC0zMmwxNC0xMkMyIDE0IDAgMiA2NCAyQzYwIDIgNTggMTQgNTggMTRsL
TE0IDEybDggMzJsLTcuNSA0TDMyIDQ2IiBmaWxsPSIjRkY4QzAwIiBzdHJva2U9IiMzMzMiIHN0
cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==
"""

def get_fox_icon():
    data = QByteArray.fromBase64(FOX_SVG.encode())
    pixmap = QPixmap()
    pixmap.loadFromData(data)
    return QIcon(pixmap)