"""
图片测量工具 - 主入口文件
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from PIL import Image, ImageTk

from src.core.app import ImageMeasureApp
from src.ui.styles.manager import StyleManager
from src.config.settings import Config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="image-measure",
        description="图像像素距离测量工具",
    )
    parser.add_argument(
        "--project",
        metavar="PATH",
        help="启动时自动加载的 .project.json 项目文件",
    )
    parser.add_argument(
        "--folder",
        metavar="PATH",
        help="启动时自动加载的图片文件夹",
    )
    args = parser.parse_args()

    root = tk.Tk()
    style_manager = StyleManager("ui_styles.json")
    app = ImageMeasureApp(root)

    if args.project:
        try:
            from src.persistence.file_handler import FileHandler
            project_data = FileHandler.load_project(args.project)
            if project_data:
                from src.core.commands import load_project_data
                load_project_data(app, project_data)
                if app.image_paths:
                    app.load_image()
        except Exception as e:
            print(f"加载项目失败: {e}")

    if args.folder and os.path.isdir(args.folder):
        from src.core.constants import IMAGE_EXTS
        try:
            files = sorted(
                os.path.join(args.folder, f)
                for f in os.listdir(args.folder)
                if f.lower().endswith(IMAGE_EXTS)
            )
            if files:
                app.image_paths = files
                app.index = 0
                app.load_image()
        except Exception as e:
            print(f"加载文件夹失败: {e}")

    root.mainloop()


if __name__ == "__main__":
    main()
