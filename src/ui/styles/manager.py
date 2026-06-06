"""
样式管理器模块
"""
import json
import os
from typing import Dict, Any


class StyleManager:
    """样式管理器"""
    
    def __init__(self, style_file='ui_styles.json'):
        self.style_file = style_file
        self.styles = self._load_styles()
    
    def _load_styles(self) -> Dict[str, Any]:
        """加载样式配置"""
        try:
            with open(self.style_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_styles()
        except json.JSONDecodeError:
            return self._get_default_styles()
    
    def _get_default_styles(self) -> Dict[str, Any]:
        """获取默认样式（字段名与 ui_styles.json 对齐）。"""
        return {
            'colors': {
                'main_background': '#FAFAFA',
                'toolbar': '#F3F2F1',
                'toolbar_shadow': '#E1DFDD',
                'button': '#FFFFFF',
                'button_hover': '#E1DFDD',
                'button_active': '#E1DFDD',
                'text': '#323130',
                'text_hover': '#323130',
                'text_active': '#323130',
                'tooltip_background': '#323130',
                'tooltip_text': '#FFFFFF',
                'menu_active': '#0078D4',
                'menu_active_text': '#FFFFFF',
            },
            'fonts': {
                'family': 'Segoe UI',
                'size': 11,
                'tooltip_size': 9,
            },
            'spacing': {
                'button_padx': 8,
                'button_pady': 2,
                'button_large_padx': 8,
                'button_large_pady': 6,
                'group_padx': 2,
                'toolbar_padx': 8,
                'toolbar_pady': 6,
                'toolbar_min_padx': 12,
                'toolbar_base_padx': 24,
                'status_padx': 8,
                'status_pady': 6,
                'tooltip_padx': 8,
                'tooltip_pady': 4,
            },
            'sizes': {
                'button_width': 4,
                'button_height': 23,
                'button_large_height': 68,
                'toolbar_shadow_height': 1,
                'scale_input_width': 6,
            },
            'scales': {
                'min_window_width': 600,
                'min_scale_factor': 0.6,
                'max_scale_factor': 1.0,
                'reference_width': 1200,
            },
        }
    
    def get_color(self, color_name: str) -> str:
        """获取颜色"""
        return self.styles.get('colors', {}).get(color_name, '#FFFFFF')
    
    def get_font(self, font_name: str) -> Any:
        """获取字体"""
        return self.styles.get('fonts', {}).get(font_name, 'Arial')
    
    def get_size(self, size_name: str) -> int:
        """获取尺寸"""
        return self.styles.get('sizes', {}).get(size_name, 10)
    
    def get_spacing(self, spacing_name: str) -> int:
        """获取间距"""
        return self.styles.get('spacing', {}).get(spacing_name, 10)
    
    def save_styles(self):
        """保存样式配置"""
        with open(self.style_file, 'w', encoding='utf-8') as f:
            json.dump(self.styles, f, indent=2, ensure_ascii=False)
