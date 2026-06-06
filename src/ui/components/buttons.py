"""
UI组件模块 - 按钮组件
"""
import tkinter as tk
from typing import Optional, Callable


class ModernButton(tk.Button):
    """现代化按钮组件"""

    def __init__(self, parent, text, command, color='#2B579A', priority=0,
                 size='small', style_manager=None, menu=None, **kwargs):
        self.style_manager = style_manager
        self.base_color = color
        self.original_text = text
        self.font_family = self.style_manager.get_font('family') if self.style_manager else 'Arial'
        self.size = size
        self.font_weight = 'normal'
        self.priority = priority
        self.visible = True
        self.menu = menu
        kwargs.pop('padx', None)

        if size == 'large':
            self.font_size = self.style_manager.get_font('size') if self.style_manager else 12
            button_padx = self.style_manager.get_spacing('button_large_padx') if self.style_manager else 15
            button_pady = self.style_manager.get_spacing('button_large_pady') if self.style_manager else 8
            button_height = self.style_manager.get_size('button_large_height') if self.style_manager else 40
        else:
            self.font_size = self.style_manager.get_font('size') if self.style_manager else 10
            button_padx = self.style_manager.get_spacing('button_padx') if self.style_manager else 10
            button_pady = self.style_manager.get_spacing('button_pady') if self.style_manager else 5
            button_height = self.style_manager.get_size('button_height') if self.style_manager else 32

        super().__init__(
            parent,
            text=text,
            command=command if not menu else None,
            bg=self.style_manager.get_color('button') if self.style_manager else '#FFFFFF',
            fg=self.style_manager.get_color('text') if self.style_manager else '#000000',
            relief='flat',
            padx=button_padx,
            pady=button_pady,
            font=(self.font_family, self.font_size, self.font_weight),
            cursor='hand2',
            activebackground=self.style_manager.get_color('button_active') if self.style_manager else '#E5E5E5',
            activeforeground=self.style_manager.get_color('text_active') if self.style_manager else '#000000',
            borderwidth=0,
            highlightthickness=0,
            anchor='center',
            width=self.style_manager.get_size('button_width') if self.style_manager else 8,
            **kwargs
        )
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        if self.original_text:
            from src.ui.components.tooltips import ToolTip
            ToolTip(self, self.original_text, self.style_manager)

    def _on_enter(self, event):
        """鼠标悬停事件"""
        self.config(bg=self.style_manager.get_color('button_hover') if self.style_manager else '#F5F5F5')

    def _on_leave(self, event):
        """鼠标离开事件"""
        self.config(bg=self.style_manager.get_color('button') if self.style_manager else '#FFFFFF')

    def _on_click(self, event=None):
        """点击事件"""
        if self.menu:
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            self.menu.post(x, y)

    def update_font(self, scale_factor):
        """更新字体大小"""
        new_font_size = int(self.font_size * scale_factor)
        self.config(font=(self.font_family, new_font_size, self.font_weight))

    def update_padding(self, scale_factor):
        """更新内边距"""
        pass

    def set_visible(self, visible):
        """设置可见性"""
        self.visible = visible
        if visible:
            self.pack()
        else:
            self.pack_forget()
