"""应用配置"""
import os


class Config:
    """应用配置类（硬编码兜底值，外部可改 ui_styles.json 覆盖视觉部分）。"""

    # 指向项目根（src/config -> src -> 项目根）
    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    UI = {
        "min_window_width": 600,
        "reference_width": 1200,
        "min_scale_factor": 0.6,
        "max_scale_factor": 1.0,
    }

    IMAGE = {
        "min_scale": 0.1,
        "max_scale": 5.0,
        "default_scale": 1.0,
    }

    EXPORT = {
        "default_format": "csv",
        "supported_formats": ["csv", "json", "excel"],
    }

    MEASUREMENT = {
        "default_unit": "px",
        "dpi": 96,
    }

    FILE = {
        "segment_suffix": "_segments.json",
        "project_suffix": ".project.json",
        "export_suffix": "_measurements.csv",
    }

    # 单一来源
    UNITS = ("px", "mm", "cm", "in")

    @classmethod
    def get_units(cls):
        return list(cls.UNITS)
