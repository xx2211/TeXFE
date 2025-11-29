from dataclasses import dataclass, field
from pathlib import Path
import sys


def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AppConfig:
    # 路径配置
    ROOT_DIR: Path = get_base_path()
    ASSETS_DIR: Path = ROOT_DIR / "assets"

    # ✅ 【补上了这一行】 热键配置
    # 格式参考 keyboard 库： "alt+q", "ctrl+shift+a" 等
    HOTKEY: str = "alt+q"

    # 模型路径字典
    MODEL_PATHS: dict = field(default=None)

    def __post_init__(self):
        # 初始化模型路径字典
        paths = {
            'image_resizer': str(self.ASSETS_DIR / 'image_resizer.onnx'),
            'encoder': str(self.ASSETS_DIR / 'encoder.onnx'),
            'decoder': str(self.ASSETS_DIR / 'decoder.onnx'),
            'tokenizer': str(self.ASSETS_DIR / 'tokenizer.json'),
        }
        # 绕过 frozen=True 限制赋值
        object.__setattr__(self, 'MODEL_PATHS', paths)