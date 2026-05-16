"""
图片测量工具 - 主入口文件
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from PIL import Image, ImageTk

from src.core.app import ImageMeasureApp
from src.ui.styles.manager import StyleManager
from src.config.settings import Config


def main():
    """主函数"""
    root = tk.Tk()
    
    style_manager = StyleManager('ui_styles.json')
    app = ImageMeasureApp(root)
    
    root.mainloop()


if __name__ == '__main__':
    main()
