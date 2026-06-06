"""字体加载工具，统一 fallback。"""
from functools import lru_cache
from PIL import ImageFont


@lru_cache(maxsize=8)
def get_font(size: int):
    """尝试加载 arial.ttf，失败回退到默认字体。"""
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()
