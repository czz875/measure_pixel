"""
UI组件模块 - 标签组件
"""
import tkinter as tk
from typing import Optional


class ResponsiveLabel(tk.Label):
    """响应式标签组件"""
    
    def __init__(self, parent, text, font_family='Arial', font_size=10, 
                 style_manager=None, **kwargs):
        self.style_manager = style_manager
        self.original_text = text
        self.font_family = font_family
        self.font_size = font_size
        self.base_font_size = font_size
        
        super().__init__(
            parent,
            text=text,
            font=(font_family, font_size),
            **kwargs
        )
    
    def update_font(self, scale_factor):
        """更新字体大小"""
        new_font_size = int(self.base_font_size * scale_factor)
        self.config(font=(self.font_family, new_font_size))
    
    def update_padding(self, scale_factor):
        """更新内边距"""
        pass
    
    def set_text(self, text):
        """设置文本"""
        self.config(text=text)
