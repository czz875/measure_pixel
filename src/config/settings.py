"""
应用配置文件
"""
import os

class Config:
    """应用配置类"""
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    UI = {
        'min_window_width': 400,
        'reference_width': 1200,
        'min_scale_factor': 0.6,
        'max_scale_factor': 1.0,
    }
    
    IMAGE = {
        'min_scale': 0.1,
        'max_scale': 5.0,
        'default_scale': 1.0,
    }
    
    EXPORT = {
        'default_format': 'csv',
        'supported_formats': ['csv', 'json', 'excel'],
    }
    
    MEASUREMENT = {
        'default_unit': 'px',
        'supported_units': ['px', 'mm', 'cm', 'inch'],
        'dpi': 96,  # 默认DPI
    }
    
    FILE = {
        'segment_suffix': '_segments.json',
        'project_suffix': '.project.json',
        'export_suffix': '_measurements.csv',
    }
