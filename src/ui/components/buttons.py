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
        self.short_text = self._get_short_text(text)
        self.current_text = self.short_text
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
            text=self.short_text,
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
        if self.original_text != self.short_text:
            from src.ui.components.tooltips import ToolTip
            ToolTip(self, self.original_text, self.style_manager)
    
    def _get_short_text(self, text):
        """获取短文本"""
        short_map = {
            '📁 打开': '📁',
            '⬅️ 上一张': '⬅️',
            '➡️ 下一张': '➡️',
            '💾 保存': '💾',
            '📐 测量': '📐',
            '📊 导出': '📊',
            '📦 批量导出': '📦',
            '❌ 清除': '❌',
            '+': '+',
            '-': '-',
            '↺': '↺'
        }
        return short_map.get(text, text)
    
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


class ScaleInput(tk.Entry):
    """缩放比例输入框"""
    
    def __init__(self, parent, app, style_manager=None, **kwargs):
        from src.ui.styles.manager import StyleManager
        self.style_manager = style_manager or StyleManager()
        self.app = app
        self.font_family = self.style_manager.get_font('family')
        self.font_size = self.style_manager.get_font('size')
        self.base_padx = self.style_manager.get_spacing('button_padx')
        self.current_padx = self.base_padx
        
        kwargs.pop('padx', None)
        super().__init__(
            parent,
            text='100%',
            bg=self.style_manager.get_color('button'),
            fg=self.style_manager.get_color('text'),
            font=(self.font_family, self.font_size, 'normal'),
            relief='solid',
            borderwidth=1,
            highlightthickness=0,
            width=self.style_manager.get_size('scale_input_width'),
            justify='center',
            **kwargs
        )
        self.insert(0, '100%')
        self.bind('<Return>', self._on_enter)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<FocusIn>', self._on_focus_in)
    
    def _on_enter(self, event):
        self._apply_scale()
    
    def _on_focus_out(self, event):
        self._apply_scale()
    
    def _on_focus_in(self, event):
        self.select_range(0, 'end')
    
    def _apply_scale(self):
        text = self.get().strip()
        try:
            if text.endswith('%'):
                value = float(text[:-1])
            else:
                value = float(text)
            
            if value < 10:
                value = 10
            elif value > 500:
                value = 500
            
            self.app.set_scale(value / 100)
            self.delete(0, 'end')
            self.insert(0, f'{int(value)}%')
        except ValueError:
            self.delete(0, 'end')
            self.insert(0, f'{int(self.app.scale_factor * 100)}%')
    
    def update_scale(self, scale_factor):
        value = int(scale_factor * 100)
        self.delete(0, 'end')
        self.insert(0, f'{value}%')
    
    def update_font(self, font_size):
        self.font_size = font_size
        self.config(font=(self.font_family, self.font_size, 'normal'))
    
    def update_padding(self, padx, pady):
        pass
