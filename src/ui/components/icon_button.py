"""
UI组件模块 - 图标按钮组件
"""
import tkinter as tk
from tkinter import Menu
from typing import Optional, Callable, List, Tuple


class IconButton(tk.Button):
    """图标按钮组件"""
    
    def __init__(self, parent, icon, command=None, tooltip=None, 
                 menu_items=None, style_manager=None, **kwargs):
        self.style_manager = style_manager
        self.icon = icon
        self.tooltip = tooltip
        self.menu_items = menu_items
        self.menu = None
        self.menu_item_configs = []
        self.active_menu_item = None
        
        bg_color = self.style_manager.get_color('button') if self.style_manager else '#FFFFFF'
        fg_color = self.style_manager.get_color('text') if self.style_manager else '#323130'
        hover_color = self.style_manager.get_color('button_hover') if self.style_manager else '#E1DFDD'
        active_color = self.style_manager.get_color('button_active') if self.style_manager else '#E1DFDD'
        font_family = self.style_manager.get_font('family') if self.style_manager else 'Segoe UI'
        font_size = self.style_manager.get_font('size') if self.style_manager else 11
        
        kwargs.pop('bg', None)
        kwargs.pop('fg', None)
        kwargs.pop('font', None)
        
        super().__init__(
            parent,
            text=icon,
            command=command if not menu_items else self._show_menu,
            bg=bg_color,
            fg=fg_color,
            font=(font_family, font_size),
            relief='flat',
            borderwidth=0,
            padx=8,
            pady=4,
            cursor='hand2',
            **kwargs
        )
        
        self.hover_color = hover_color
        self.active_color = active_color
        self.default_bg = bg_color
        self.highlight_bg = '#0078D4'
        self.highlight_fg = '#FFFFFF'
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        if self.menu_items:
            self._create_menu()
        
        if self.tooltip:
            from src.ui.components.tooltips import ToolTip
            ToolTip(self, self.tooltip, self.style_manager)
    
    def _create_menu(self):
        """创建二级菜单"""
        self.menu = Menu(self, tearoff=0)
        
        for item in self.menu_items:
            if isinstance(item, str):
                self.menu.add_command(label=item, command=lambda x=item: self._on_menu_click(x))
                self.menu_item_configs.append({'label': item, 'index': len(self.menu_item_configs)})
            elif isinstance(item, tuple) and len(item) == 2:
                icon, text = item
                self.menu.add_command(label=f"{icon} {text}", command=lambda x=text: self._on_menu_click(x))
                self.menu_item_configs.append({'label': text, 'index': len(self.menu_item_configs)})
            elif isinstance(item, dict):
                label = item.get('label', '')
                icon = item.get('icon', '')
                command = item.get('command')
                full_label = f"{icon} {label}" if icon else label
                self.menu.add_command(label=full_label, command=command)
                self.menu_item_configs.append({'label': label, 'index': len(self.menu_item_configs), 'command': command})
    
    def _show_menu(self):
        """显示菜单"""
        if self.menu:
            self._update_menu_styles()
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            self.menu.post(x, y)
    
    def _on_menu_click(self, item):
        """菜单项点击事件"""
        if hasattr(self, 'menu_callback'):
            self.menu_callback(item)
    
    def set_menu_callback(self, callback):
        """设置菜单回调函数"""
        self.menu_callback = callback
    
    def _on_enter(self, event):
        """鼠标悬停事件"""
        self.config(bg=self.hover_color)
    
    def _on_leave(self, event):
        """鼠标离开事件"""
        self.config(bg=self.default_bg)
    
    def set_icon(self, icon):
        """设置图标"""
        self.config(text=icon)
        self.icon = icon
    
    def set_tooltip(self, tooltip):
        """设置提示文字"""
        self.tooltip = tooltip
    
    def set_active_menu_item(self, label):
        """设置当前激活的菜单项（高亮显示）"""
        self.active_menu_item = label
        self._update_menu_styles()
    
    def _update_menu_styles(self):
        """更新菜单项的样式"""
        if not self.menu:
            return
        
        for config in self.menu_item_configs:
            index = config['index']
            label = config['label']
            
            if label == self.active_menu_item:
                self.menu.entryconfig(index, background=self.highlight_bg, foreground=self.highlight_fg)
            else:
                self.menu.entryconfig(index, background='', foreground='')