from ..base_engine import BaseEngine
from rapid_latex_ocr import LaTeXOCR


class RapidEngine(BaseEngine):
    def __init__(self, config):
        self.model = None
        # 我们可以选择在初始化时自动加载
        # 也可以留给外部显式调用。为了 MVP 简单，我们这里直接调用。
        self.load_model(config.ASSETS_DIR)

    def load_model(self, assets_dir):
        print(f"正在加载模型，路径: {assets_dir}")
        self.model = LaTeXOCR(
            image_resizer_path=str(assets_dir / 'image_resizer.onnx'),
            encoder_path=str(assets_dir / 'encoder.onnx'),
            decoder_path=str(assets_dir / 'decoder.onnx'),
            tokenizer_json=str(assets_dir / 'tokenizer.json')
        )

    def recognize(self, image_data: bytes) -> str:
        if self.model is None:
            return "模型未加载"

        # ✅ 新增：空数据检查
        if not image_data or len(image_data) == 0:
            return "错误：接收到的图片数据为空"

        try:
            result, _ = self.model(image_data)
            return result
        except Exception as e:
            # 打印详细错误栈，防止直接闪退
            import traceback
            traceback.print_exc()
            return f"识别核心错误: {str(e)}"
