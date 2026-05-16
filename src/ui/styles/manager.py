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
        """获取默认样式"""
        return {
            'colors': {
                'button': '#FFFFFF',
                'button_hover': '#F5F5F5',
                'button_active': '#E5E5E5',
                'text': '#000000',
                'text_active': '#000000',
                'menu_active': '#2B579A',
                'menu_active_text': '#FFFFFF',
                'tooltip_bg': '#333333',
                'tooltip_fg': '#FFFFFF',
                'toolbar_bg': '#F3F2F1',
                'status_bar_bg': '#F3F2F1'
            },
            'fonts': {
                'family': 'Arial',
                'size': 10
            },
            'sizes': {
                'button_width': 8,
                'button_height': 32,
                'button_large_height': 40
            },
            'spacing': {
                'button_padx': 10,
                'button_pady': 5,
                'button_large_padx': 15,
                'button_large_pady': 8
            }
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
