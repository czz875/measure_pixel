"""
UI组件模块 - 提示框组件
"""
import tkinter as tk


class ToolTip:
    """提示框组件"""
    
    def __init__(self, widget, text, style_manager=None):
        self.widget = widget
        self.text = text
        self.style_manager = style_manager
        self.tip_window = None
        
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)
    
    def show_tip(self, event=None):
        """显示提示框"""
        if self.tip_window or not self.text:
            return
        
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        bg_color = self.style_manager.get_color('tooltip_background') if self.style_manager else '#333333'
        fg_color = self.style_manager.get_color('tooltip_text') if self.style_manager else '#FFFFFF'
        font_family = self.style_manager.get_font('family') if self.style_manager else 'Arial'
        font_size = self.style_manager.get_font('size') if self.style_manager else 10
        
        label = tk.Label(
            tw,
            text=self.text,
            justify='left',
            background=bg_color,
            foreground=fg_color,
            relief='solid',
            borderwidth=1,
            font=(font_family, font_size)
        )
        label.pack(ipadx=1)
    
    def hide_tip(self, event=None):
        """隐藏提示框"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
