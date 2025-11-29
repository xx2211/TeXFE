import http.server
import socketserver
import socket
import threading
import cgi
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class ServerSignals(QObject):
    image_received = pyqtSignal(bytes)


class MobileHandler(http.server.BaseHTTPRequestHandler):
    # 静态变量，存储 HTML 路径
    HTML_PATH = None

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        # ✅ 【调试代码】打印出它在找的绝对路径
        # print(f"🔍 [Server] 正在寻找 HTML 文件: {self.HTML_PATH}")
        # if self.HTML_PATH:
        #     print(f"   -> 文件是否存在? {self.HTML_PATH.exists()}")

        # ✅ 读取 HTML 文件
        if self.HTML_PATH and self.HTML_PATH.exists():
            with open(self.HTML_PATH, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.wfile.write(b"Error: HTML file not found.")

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            fields = cgi.parse_multipart(self.rfile, pdict)

            if 'file' in fields:
                img_data = fields['file'][0]
                if hasattr(self.server, 'signals'):
                    self.server.signals.image_received.emit(img_data)

                self.send_response(200)
                self.end_headers()
                self.wfile.write("OK".encode('utf-8'))
                return

        self.send_response(400)
        self.end_headers()


class BridgeServer:
    def __init__(self, templates_dir: Path, port=8989):
        self.port = port
        self.signals = ServerSignals()
        self.httpd = None
        self.thread = None

        # ✅ 把 HTML 路径传给 Handler 类
        MobileHandler.HTML_PATH = templates_dir / "upload.html"

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start(self):
        if self.httpd:
            return self._get_url()

        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("", self.port), MobileHandler)
        self.httpd.signals = self.signals

        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()

        return self._get_url()

    def _get_url(self):
        ip = self.get_local_ip()
        return f"http://{ip}:{self.port}"

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None