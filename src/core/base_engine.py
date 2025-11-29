from abc import ABC, abstractmethod
from pathlib import Path


# 这是一个抽象类，它不干活，只定规矩
class BaseEngine(ABC):

    @abstractmethod
    def load_model(self, assets_dir: Path):
        """加载模型"""
        pass

    @abstractmethod
    def recognize(self, image_data) -> str:
        """核心推理接口"""
        pass
