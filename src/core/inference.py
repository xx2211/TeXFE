import onnxruntime as ort
import numpy as np
from . import image_utils, tokenizer
from ..config import AppConfig


class InferenceEngine:
    def __init__(self, config: AppConfig):
        self.cfg = config
        # 加载模型 (耗时操作，只做一次)
        print(f"Loading model from {self.cfg.MODEL_PATH}...")
        self.session = ort.InferenceSession(str(self.cfg.MODEL_PATH))
        self.tokenizer = tokenizer.load(self.cfg.TOKENIZER_PATH)

    def recognize(self, image_data) -> str:
        """
        输入: 原始图片 (OpenCV格式 或 Bytes)
        输出: LaTeX 字符串
        """
        # 1. 预处理 (调用 image_utils 里的纯函数)
        tensor = image_utils.preprocess(image_data, self.cfg.INPUT_SIZE)

        # 2. 推理
        # 注意：这里简化了，实际可能是 encoder-decoder 循环
        outputs = self.session.run(None, {"input": tensor})

        # 3. 解码
        latex = self.tokenizer.decode(outputs[0])
        return latex
