"""
核心应用类 - 图片测量工具主逻辑
"""
import os
import math
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from typing import List, Tuple, Optional, Dict
from collections import defaultdict

from src.core.models import LineSegment, AngleSegment, CircleSegment, RectangleSegment, PointToLineSegment, PolygonSegment, MeasurementData
from src.config.settings import Config
from src.persistence.file_handler import FileHandler
from src.core.history import History, HistoryState, snapshot_from_app, apply_state
from src.core.drawing import draw_annotations_on_image
from src.core.tools import (
    Tool,
    switch_mode as tools_switch_mode,
    add_point as tools_add_point,
    finish as tools_finish,
    current_mode as tools_current_mode,
    get_active_label as tools_get_active_label,
)
from src.core.commands import (
    export_lengths_to_csv,
    batch_export_all,
    build_project_data,
    load_project_data,
)
from src.core.constants import (
    UNIT_CONVERSION,
    MIN_SCALE,
    MAX_SCALE,
    SCALE_STEP,
)


IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')
SAVE_SUFFIX = '_measured'


class ImageMeasureApp:
    """图片测量应用核心类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title('图像像素距离测量工具')
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        min_width = max(600, int(screen_width / 20))
        min_height = max(400, int(screen_height / 20))
        self.root.minsize(min_width, min_height)
        self.root.geometry('1200x800')

        self.image_paths = []
        self.index = -1
        self.orig_image = None
        self.display_image = None
        self.current_points = []
        self.all_segments = []
        self.all_angles = []
        self.all_circles = []
        self.all_rectangles = []
        self.all_point_to_lines = []
        self.all_polygons = []
        self.selected_segment = None
        self.selected_angle = None
        self.selected_circle = None
        self.selected_rectangle = None
        self.selected_point_to_line = None
        self.selected_polygon = None
        self.drag_point_index = None
        self.angle_mode = False
        self.angle_points = []
        self.circle_mode = False
        self.circle_points = []
        self.rectangle_mode = False
        self.rectangle_points = []
        self.point_to_line_mode = False
        self.point_to_line_points = []
        self.polygon_mode = False
        self.polygon_points = []
        self.pixels_per_unit = 100
        self.current_unit = "px"
        self.units = Config.get_units()
        self.unit_conversion = dict(UNIT_CONVERSION)
        self.history = History()

        self.scale_factor = 1.0
        self.min_scale = MIN_SCALE
        self.max_scale = MAX_SCALE
        self.scale_step = SCALE_STEP

        self.setup_ui()
        self.bind_keys()
    
    def setup_ui(self):
        """设置UI界面 - 极简图标布局"""
        from src.ui.components.icon_button import IconButton
        from src.ui.components.tooltips import ToolTip
        from src.ui.components.labels import ResponsiveLabel
        from src.ui.styles.manager import StyleManager
        
        self.style_manager = StyleManager('ui_styles.json')
        
        main_frame = tk.Frame(self.root, bg=self.style_manager.get_color('main_background'))
        main_frame.pack(fill='both', expand=True)
        self.main_frame = main_frame
        
        toolbar = tk.Frame(main_frame, bg=self.style_manager.get_color('toolbar'), height=48)
        toolbar.pack(side='top', fill='x')
        self.toolbar = toolbar
        
        toolbar_shadow = tk.Frame(toolbar, bg=self.style_manager.get_color('toolbar_shadow'),
                                height=1)
        toolbar_shadow.pack(side='bottom', fill='x')
        
        toolbar_content = tk.Frame(toolbar, bg=self.style_manager.get_color('toolbar'))
        toolbar_content.pack(fill='both', expand=True, padx=12, pady=8)
        self.toolbar_content = toolbar_content
        
        left_section = tk.Frame(toolbar_content, bg=self.style_manager.get_color('toolbar'))
        left_section.pack(side='left', fill='y')
        self.left_section = left_section
        
        file_menu_items = [
            {'icon': '📷', 'label': '打开图片', 'command': self.open_image},
            {'icon': '📁', 'label': '打开文件夹', 'command': self.open_folder},
            {'icon': '💾', 'label': '保存项目', 'command': self.save_project},
            {'icon': '📂', 'label': '加载项目', 'command': self.load_project}
        ]
        btn = IconButton(left_section, icon='📁', tooltip='文件', 
                         menu_items=file_menu_items, style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 4))
        
        btn = IconButton(left_section, icon='⏪', tooltip='撤销', 
                         command=self.undo, style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 4))
        
        btn = IconButton(left_section, icon='⏩', tooltip='恢复', 
                         command=self.redo, style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 4))
        
        measure_menu_items = [
            {'icon': '📏', 'label': '测量距离', 'command': self.enable_length_mode},
            {'icon': '📐', 'label': '测量角度', 'command': self.enable_angle_mode},
            {'icon': '⭕', 'label': '测量圆形', 'command': self.enable_circle_mode},
            {'icon': '⬜', 'label': '测量矩形', 'command': self.enable_rectangle_mode},
            {'icon': '📏', 'label': '点到线距离', 'command': self.enable_point_to_line_mode},
            {'icon': '🔷', 'label': '多边形测面积', 'command': self.enable_polygon_mode}
        ]
        self.measure_btn = IconButton(left_section, icon='📐', tooltip='测量', 
                         menu_items=measure_menu_items, style_manager=self.style_manager)
        self.measure_btn.pack(side='left', padx=(0, 4))
        
        export_menu_items = [
            {'icon': '📄', 'label': '导出CSV', 'command': self.export_lengths},
            {'icon': '📤', 'label': '导出图片', 'command': self.save_annotated},
            {'icon': '📦', 'label': '批量导出', 'command': self.batch_export}
        ]
        btn = IconButton(left_section, icon='📊', tooltip='导出', 
                         menu_items=export_menu_items, style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 4))
        
        btn = IconButton(left_section, icon='⬅️', tooltip='上一张', 
                         command=self.prev_image, style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 4))
        
        btn = IconButton(left_section, icon='➡️', tooltip='下一张', 
                         command=self.next_image, style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 4))
        
        btn = IconButton(left_section, icon='❌', tooltip='清除', 
                         command=self.clear_all_annotations, style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 4))

        content_area = tk.Frame(main_frame, bg=self.style_manager.get_color('main_background'))
        content_area.pack(fill='both', expand=True, padx=8, pady=8)
        self.content_area = content_area
        
        canvas_container = tk.Frame(content_area, bg=self.style_manager.get_color('button'), relief='flat', bd=0)
        canvas_container.pack(fill='both', expand=True)
        self.canvas_container = canvas_container
        
        self.canvas = tk.Canvas(canvas_container, cursor='cross', bg=self.style_manager.get_color('main_background'), 
                               highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=2, pady=2)
        self.canvas.bind('<Button-1>', self.on_left_click)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Configure>', lambda e: self.redraw())

        status_bar = tk.Frame(self.root, bg=self.style_manager.get_color('toolbar'), height=32)
        status_bar.pack(side='bottom', fill='x')
        self.status_bar = status_bar
        
        status_shadow = tk.Frame(status_bar, bg=self.style_manager.get_color('toolbar_shadow'),
                                height=1)
        status_shadow.pack(side='top', fill='x')
        
        status_content = tk.Frame(status_bar, bg=self.style_manager.get_color('toolbar'))
        status_content.pack(fill='both', expand=True, padx=12, pady=4)
        
        self.status = ResponsiveLabel(status_content, style_manager=self.style_manager,
                                     text='未加载图片', bd=0, relief='flat', anchor='w',
                                     bg=self.style_manager.get_color('toolbar'),
                                     fg=self.style_manager.get_color('text'))
        self.status.pack(side='left', fill='x', expand=True)
        
        right_section = tk.Frame(status_content, bg=self.style_manager.get_color('toolbar'))
        right_section.pack(side='right')
        
        btn = IconButton(right_section, icon='−', tooltip='缩小', 
                         command=lambda: self.zoom(0.9), style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 2))
        
        self.scale_label = ResponsiveLabel(right_section, style_manager=self.style_manager,
                                          text='100%', bg=self.style_manager.get_color('button'),
                                          fg=self.style_manager.get_color('text'),
                                          padx=8, pady=2)
        self.scale_label.pack(side='left', padx=(0, 2))
        
        btn = IconButton(right_section, icon='+', tooltip='放大', 
                         command=lambda: self.zoom(1.1), style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 2))
        
        btn = IconButton(right_section, icon='↺', tooltip='重置', 
                         command=self.reset_scale, style_manager=self.style_manager)
        btn.pack(side='left', padx=(0, 8))
        
        unit_label = ResponsiveLabel(right_section, style_manager=self.style_manager,
                                    text='单位:', bg=self.style_manager.get_color('toolbar'),
                                    fg=self.style_manager.get_color('text'))
        unit_label.pack(side='left', padx=(0, 4))
        
        self.unit_var = tk.StringVar(value=self.current_unit)
        self.unit_menu = tk.OptionMenu(right_section, self.unit_var, *self.units,
                                       command=self._on_unit_change)
        self.unit_menu.config(bg=self.style_manager.get_color('button'),
                             fg=self.style_manager.get_color('text'),
                             activebackground=self.style_manager.get_color('menu_active'),
                             activeforeground=self.style_manager.get_color('menu_active_text'),
                             font=(self.style_manager.get_font('family'),
                                   self.style_manager.get_font('size'),
                                   'normal'),
                             relief='flat',
                             borderwidth=0,
                             highlightthickness=0,
                             padx=4,
                             pady=2,
                             indicatoron=0,
                             direction='below')
        self.unit_menu.pack(side='left')
    
    def bind_keys(self):
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<space>', lambda e: self.start_new_segment())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.root.bind('<s>', lambda e: self.save_annotated())
        self.root.bind('<MouseWheel>', self._on_mousewheel)
        
        def undo_handler(event):
            self.undo()
            return 'break'
        
        def redo_handler(event):
            self.redo()
            return 'break'
        
        self.root.bind('<Control-z>', undo_handler)
        self.root.bind('<Control-y>', redo_handler)

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom(1.1)
        else:
            self.zoom(0.9)

    def _get_current_annotations(self):
        """获取当前图片的所有标注（线段、角度、圆形、矩形、点到线、多边形）"""
        segments = [s for s in self.all_segments if s.image_index == self.index]
        angles = [a for a in self.all_angles if a.image_index == self.index]
        circles = [c for c in self.all_circles if c.image_index == self.index]
        rectangles = [r for r in self.all_rectangles if r.image_index == self.index]
        point_to_lines = [ptl for ptl in self.all_point_to_lines if ptl.image_index == self.index]
        polygons = [p for p in self.all_polygons if p.image_index == self.index]
        return segments, angles, circles, rectangles, point_to_lines, polygons

    def _save_current_annotations(self):
        """保存当前图片的所有标注"""
        if not self.image_paths or self.index < 0:
            return
        segments, angles, circles, rectangles, point_to_lines, polygons = self._get_current_annotations()
        measurement_data = MeasurementData(segments=segments, angles=angles, 
                                         circles=circles, rectangles=rectangles, 
                                         point_to_lines=point_to_lines, polygons=polygons)
        FileHandler.save_segments(FileHandler.get_segment_file_path(self.image_paths[self.index]), measurement_data)

    def _add_annotation(self, annotation):
        """添加标注（线段、角度、圆形、矩形、点到线、多边形）"""
        if isinstance(annotation, LineSegment):
            self.all_segments.append(annotation)
        elif isinstance(annotation, AngleSegment):
            self.all_angles.append(annotation)
        elif isinstance(annotation, CircleSegment):
            self.all_circles.append(annotation)
        elif isinstance(annotation, RectangleSegment):
            self.all_rectangles.append(annotation)
        elif isinstance(annotation, PointToLineSegment):
            self.all_point_to_lines.append(annotation)
        elif isinstance(annotation, PolygonSegment):
            self.all_polygons.append(annotation)
        self.save_state()
        self._save_current_annotations()
        self.redraw()
        self.update_status()

    def _delete_annotation(self, annotation):
        """删除标注（线段、角度、圆形、矩形、点到线、多边形）"""
        if isinstance(annotation, LineSegment):
            self.all_segments.remove(annotation)
            self.selected_segment = None
        elif isinstance(annotation, AngleSegment):
            self.all_angles.remove(annotation)
            self.selected_angle = None
        elif isinstance(annotation, CircleSegment):
            self.all_circles.remove(annotation)
            self.selected_circle = None
        elif isinstance(annotation, RectangleSegment):
            self.all_rectangles.remove(annotation)
            self.selected_rectangle = None
        elif isinstance(annotation, PointToLineSegment):
            self.all_point_to_lines.remove(annotation)
            self.selected_point_to_line = None
        elif isinstance(annotation, PolygonSegment):
            self.all_polygons.remove(annotation)
            self.selected_polygon = None
        self.save_state()
        self._save_current_annotations()
        self.redraw()
        self.update_status()

    def _clear_current_annotations(self):
        """清除当前图片的所有标注"""
        self.all_segments = [s for s in self.all_segments if s.image_index != self.index]
        self.all_angles = [a for a in self.all_angles if a.image_index != self.index]
        self.all_circles = [c for c in self.all_circles if c.image_index != self.index]
        self.all_rectangles = [r for r in self.all_rectangles if r.image_index != self.index]
        self.all_point_to_lines = [ptl for ptl in self.all_point_to_lines if ptl.image_index != self.index]
        self.all_polygons = [p for p in self.all_polygons if p.image_index != self.index]
        self.current_points = []
        self.angle_points = []
        self.circle_points = []
        self.rectangle_points = []
        self.point_to_line_points = []
        self.polygon_points = []
        self.selected_segment = None
        self.selected_angle = None
        self.selected_circle = None
        self.selected_rectangle = None
        self.selected_point_to_line = None
        self.selected_polygon = None
        self.save_state()
        self._save_current_annotations()
        self.redraw()
        self.update_status()

    def open_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        files = sorted([os.path.join(folder, f) for f in os.listdir(folder)
                        if os.path.splitext(f)[1].lower() in IMAGE_EXTS])
        if not files:
            messagebox.showinfo('提示', '该文件夹中未找到支持的图片文件。')
            return
        self.image_paths = files
        self.index = 0
        self.load_image()

    def open_image(self):
        file = filedialog.askopenfilename(filetypes=[('图片文件', '*.png *.jpg *.jpeg *.bmp *.tif *.tiff')])
        if not file:
            return
        self.image_paths = [file]
        self.index = 0
        self.load_image()

    def load_image(self):
        if not (0 <= self.index < len(self.image_paths)):
            return
        path = self.image_paths[self.index]
        try:
            self.orig_image = Image.open(path).convert('RGB')
        except Exception as e:
            messagebox.showerror('错误', f'无法打开图片：{path}\n{e}')
            return
        
        self.current_points = []
        self.angle_points = []
        self.circle_points = []
        self.rectangle_points = []
        self.point_to_line_points = []
        self.polygon_points = []
        self.selected_segment = None
        self.selected_angle = None
        self.selected_circle = None
        self.selected_rectangle = None
        self.selected_point_to_line = None
        self.selected_polygon = None

        measurement_data = FileHandler.load_segments(FileHandler.get_segment_file_path(path))
        if measurement_data:
            self.all_segments = [s for s in self.all_segments if s.image_index != self.index]
            self.all_segments.extend(measurement_data.segments)
            self.all_angles = [a for a in self.all_angles if a.image_index != self.index]
            self.all_angles.extend(measurement_data.angles)
            self.all_circles = [c for c in self.all_circles if c.image_index != self.index]
            self.all_circles.extend(measurement_data.circles)
            self.all_rectangles = [r for r in self.all_rectangles if r.image_index != self.index]
            self.all_rectangles.extend(measurement_data.rectangles)
            self.all_point_to_lines = [ptl for ptl in self.all_point_to_lines if ptl.image_index != self.index]
            self.all_point_to_lines.extend(measurement_data.point_to_lines)
            self.all_polygons = [p for p in self.all_polygons if p.image_index != self.index]
            self.all_polygons.extend(measurement_data.polygons)

        self.redraw()
        self.update_status()
        self.save_state()

    def redraw(self):
        self.canvas.delete('all')
        if not self.orig_image:
            return

        overlay = draw_annotations_on_image(
            self.orig_image,
            self,
            self.scale_factor,
            self.get_unit_display,
            self.calculate_angle,
        )
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.display_image = ImageTk.PhotoImage(overlay)
        self.canvas.create_image((cw // 2, ch // 2), image=self.display_image, anchor='center')

    def image_coord_from_canvas(self, cx, cy):
        if not self.orig_image:
            return None
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        iw, ih = self.orig_image.size
        disp_w, disp_h = self.display_size
        x0 = (cw - disp_w)//2
        y0 = (ch - disp_h)//2
        ix = (cx - x0)*iw/disp_w
        iy = (cy - y0)*ih/disp_h
        ix = max(0, min(iw-1, ix))
        iy = max(0, min(ih-1, iy))
        return (ix, iy)

    def on_left_click(self, event):
        coords = self.image_coord_from_canvas(event.x, event.y)
        if coords is None:
            return
        
        if self.angle_mode:
            angle = self.pick_angle(coords, tol=5)
            if angle:
                self.selected_angle = angle
                self.selected_segment = None
                self.drag_point_index = self.pick_angle_point(coords, angle, tol=5)
            else:
                self.selected_angle = None
                self.add_angle_point(coords)
            self.redraw()
            self.update_status()
            return

        if self.circle_mode:
            circle = self.pick_circle(coords, tol=5)
            if circle:
                self.selected_circle = circle
                self.selected_segment = None
                self.drag_point_index = self.pick_circle_point(coords, circle, tol=5)
            else:
                self.selected_circle = None
                self.add_circle_point(coords)
            self.redraw()
            self.update_status()
            return

        if self.rectangle_mode:
            rect = self.pick_rectangle(coords, tol=5)
            if rect:
                self.selected_rectangle = rect
                self.selected_segment = None
                self.drag_point_index = self.pick_rectangle_point(coords, rect, tol=5)
            else:
                self.selected_rectangle = None
                self.add_rectangle_point(coords)
            self.redraw()
            self.update_status()
            return

        if self.point_to_line_mode:
            ptl = self.pick_point_to_line(coords, tol=5)
            if ptl:
                self.selected_point_to_line = ptl
                self.selected_segment = None
                self.drag_point_index = self.pick_point_to_line_point(coords, ptl, tol=5)
            else:
                self.selected_point_to_line = None
                self.add_point_to_line_point(coords)
            self.redraw()
            self.update_status()
            return

        if self.polygon_mode:
            polygon = self.pick_polygon(coords, tol=5)
            if polygon:
                self.selected_polygon = polygon
                self.selected_segment = None
                self.drag_point_index = self.pick_polygon_point(coords, polygon, tol=5)
            else:
                self.selected_polygon = None
                self.add_polygon_point(coords)
            self.redraw()
            self.update_status()
            return

        seg = self.pick_segment(coords, tol=5)
        if seg:
            self.selected_segment = seg
            self.selected_angle = None
            self.drag_point_index = self.pick_point(coords, seg, tol=5)
        else:
            self.selected_segment = None
            self.current_points.append(coords)
        self.redraw()
        self.update_status()

    def on_right_click(self, event):
        if self.angle_mode and self.angle_points:
            self.angle_points.pop()
            self.redraw()
            self.update_status()
        elif self.circle_mode and self.circle_points:
            self.circle_points.pop()
            self.redraw()
            self.update_status()
        elif self.rectangle_mode and self.rectangle_points:
            self.rectangle_points.pop()
            self.redraw()
            self.update_status()
        elif self.point_to_line_mode and self.point_to_line_points:
            self.point_to_line_points.pop()
            self.redraw()
            self.update_status()
        elif self.polygon_mode and self.polygon_points:
            self.polygon_points.pop()
            self.redraw()
            self.update_status()
        elif self.current_points:
            self.current_points.pop()
            self.redraw()
            self.update_status()

    def start_new_segment(self):
        if self.angle_mode and len(self.angle_points) == 3:
            angle = AngleSegment(self.angle_points[1], self.angle_points[0], 
                                self.angle_points[2], self.index)
            self._add_annotation(angle)
            self.angle_points = []
        elif self.circle_mode and len(self.circle_points) == 2:
            circle = CircleSegment(self.circle_points[0], self.circle_points[1], self.index)
            self._add_annotation(circle)
            self.circle_points = []
        elif self.rectangle_mode and len(self.rectangle_points) == 2:
            rect = RectangleSegment(self.rectangle_points, self.index)
            self._add_annotation(rect)
            self.rectangle_points = []
        elif self.point_to_line_mode and len(self.point_to_line_points) == 3:
            ptl = PointToLineSegment(self.point_to_line_points[0], 
                                    self.point_to_line_points[1],
                                    self.point_to_line_points[2], self.index)
            self._add_annotation(ptl)
            self.point_to_line_points = []
        elif self.polygon_mode and len(self.polygon_points) >= 3:
            polygon = PolygonSegment(self.polygon_points.copy(), self.index)
            self._add_annotation(polygon)
            self.polygon_points = []
        elif len(self.current_points) >= 2:
            segment = LineSegment(self.current_points.copy(), self.index)
            self._add_annotation(segment)
            self.current_points = []
        self.redraw()
        self.update_status()

    def delete_selected(self):
        if self.selected_segment:
            self._delete_annotation(self.selected_segment)
        elif self.selected_angle:
            self._delete_annotation(self.selected_angle)
        elif self.selected_circle:
            self._delete_annotation(self.selected_circle)
        elif self.selected_rectangle:
            self._delete_annotation(self.selected_rectangle)
        elif self.selected_point_to_line:
            self._delete_annotation(self.selected_point_to_line)
        elif self.selected_polygon:
            self._delete_annotation(self.selected_polygon)

    def clear_all_annotations(self):
        self._clear_current_annotations()

    def prev_image(self):
        if not self.image_paths:
            return
        self.index = (self.index-1)%len(self.image_paths)
        self.load_image()

    def next_image(self):
        if not self.image_paths:
            return
        self.index = (self.index+1)%len(self.image_paths)
        self.load_image()

    def save_annotated(self):
        if not self.orig_image:
            return
        img = self.orig_image.copy()
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

        iw, ih = self.orig_image.size
        for seg in self.all_segments:
            if seg.image_index != self.index:
                continue
            pts = seg.points
            for i in range(len(pts)-1):
                p1, p2 = pts[i], pts[i+1]
                length = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                num_dashes = 20
                for j in range(num_dashes):
                    t1 = j/num_dashes
                    t2 = (j+0.5)/num_dashes
                    x1 = p1[0] + (p2[0]-p1[0])*t1
                    y1 = p1[1] + (p2[1]-p1[1])*t1
                    x2 = p1[0] + (p2[0]-p1[0])*t2
                    y2 = p1[1] + (p2[1]-p1[1])*t2
                    draw.line([(x1,y1),(x2,y2)], fill='white', width=2)
                midx = (p1[0]+p2[0])/2
                midy = (p1[1]+p2[1])/2
                draw.text((midx+5, midy), f"{length:.1f}px", fill='white', font=font)
            for p in pts:
                r = 5
                draw.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r), outline='red', width=3)

        path = self.image_paths[self.index]
        base, ext = os.path.splitext(path)
        newpath = base + SAVE_SUFFIX + ext
        try:
            img.save(newpath)
            messagebox.showinfo('保存', f'已保存: {newpath}')
        except Exception as e:
            messagebox.showerror('保存失败', f'无法保存: {e}')

    def update_status(self):
        if not self.image_paths:
            self.status.config(text='未加载图片')
            return
        path = self.image_paths[self.index]
        total = 0
        for seg in self.all_segments:
            if seg.image_index != self.index:
                continue
            for i in range(len(seg.points)-1):
                x1, y1 = seg.points[i]
                x2, y2 = seg.points[i+1]
                total += math.hypot(x2-x1, y2-y1)
        
        mode_text = ''
        if self.angle_mode:
            mode_text = f' | 角度模式: {len(self.angle_points)}/3点 (空格键完成)'
        elif self.circle_mode:
            mode_text = f' | 圆形模式: {len(self.circle_points)}/2点 (空格键完成)'
        elif self.rectangle_mode:
            mode_text = f' | 矩形模式: {len(self.rectangle_points)}/2点 (空格键完成)'
        elif self.point_to_line_mode:
            mode_text = f' | 点到线模式: {len(self.point_to_line_points)}/3点 (空格键完成)'
        elif self.polygon_mode:
            mode_text = f' | 多边形模式: {len(self.polygon_points)}点 (空格键完成)'
        elif len(self.current_points) > 0:
            mode_text = f' | 线段模式: {len(self.current_points)}点 (空格键完成)'
        
        self.status.config(text=f'[{self.index+1}/{len(self.image_paths)}] {os.path.basename(path)}  '
                                f'段数: {len([s for s in self.all_segments if s.image_index==self.index])}  总长: {self.get_unit_display(total)}{mode_text}')

    def pick_segment(self, pos, tol=5):
        x, y = pos
        for seg in reversed(self.all_segments):
            if seg.image_index != self.index:
                continue
            for i in range(len(seg.points)-1):
                x1, y1 = seg.points[i]
                x2, y2 = seg.points[i+1]
                if self.point_to_line_dist((x,y),(x1,y1),(x2,y2)) < tol:
                    return seg
        return None

    def pick_point(self, pos, seg, tol=5):
        x, y = pos
        for i, (px, py) in enumerate(seg.points):
            if math.hypot(px-x, py-y) < tol:
                return i
        return None

    def pick_angle(self, pos, tol=5):
        x, y = pos
        for angle in reversed(self.all_angles):
            if angle.image_index != self.index:
                continue
            vertex = angle.vertex_point
            if math.hypot(vertex[0]-x, vertex[1]-y) < tol:
                return angle
            if math.hypot(angle.point1[0]-x, angle.point1[1]-y) < tol:
                return angle
            if math.hypot(angle.point2[0]-x, angle.point2[1]-y) < tol:
                return angle
        return None

    def pick_angle_point(self, pos, angle, tol=5):
        x, y = pos
        if math.hypot(angle.vertex_point[0]-x, angle.vertex_point[1]-y) < tol:
            return 0
        if math.hypot(angle.point1[0]-x, angle.point1[1]-y) < tol:
            return 1
        if math.hypot(angle.point2[0]-x, angle.point2[1]-y) < tol:
            return 2
        return None

    def pick_circle(self, pos, tol=5):
        x, y = pos
        for circle in reversed(self.all_circles):
            if circle.image_index != self.index:
                continue
            if math.hypot(circle.center[0]-x, circle.center[1]-y) < tol:
                return circle
            if math.hypot(circle.radius_point[0]-x, circle.radius_point[1]-y) < tol:
                return circle
        return None

    def pick_circle_point(self, pos, circle, tol=5):
        x, y = pos
        if math.hypot(circle.center[0]-x, circle.center[1]-y) < tol:
            return 0
        if math.hypot(circle.radius_point[0]-x, circle.radius_point[1]-y) < tol:
            return 1
        return None

    def pick_rectangle(self, pos, tol=5):
        x, y = pos
        for rect in reversed(self.all_rectangles):
            if rect.image_index != self.index:
                continue
            for p in rect.points:
                if math.hypot(p[0]-x, p[1]-y) < tol:
                    return rect
        return None

    def pick_rectangle_point(self, pos, rect, tol=5):
        x, y = pos
        for i, p in enumerate(rect.points):
            if math.hypot(p[0]-x, p[1]-y) < tol:
                return i
        return None

    def pick_point_to_line(self, pos, tol=5):
        x, y = pos
        for ptl in reversed(self.all_point_to_lines):
            if ptl.image_index != self.index:
                continue
            if math.hypot(ptl.point[0]-x, ptl.point[1]-y) < tol:
                return ptl
            if math.hypot(ptl.line_start[0]-x, ptl.line_start[1]-y) < tol:
                return ptl
            if math.hypot(ptl.line_end[0]-x, ptl.line_end[1]-y) < tol:
                return ptl
        return None

    def pick_point_to_line_point(self, pos, ptl, tol=5):
        x, y = pos
        if math.hypot(ptl.point[0]-x, ptl.point[1]-y) < tol:
            return 0
        if math.hypot(ptl.line_start[0]-x, ptl.line_start[1]-y) < tol:
            return 1
        if math.hypot(ptl.line_end[0]-x, ptl.line_end[1]-y) < tol:
            return 2
        return None

    def point_to_line_dist(self, p, a, b):
        x0,y0 = p
        x1,y1 = a
        x2,y2 = b
        dx,dy = x2-x1, y2-y1
        if dx==0 and dy==0:
            return math.hypot(x0-x1, y0-y1)
        t = max(0,min(1,((x0-x1)*dx+(y0-y1)*dy)/(dx*dx+dy*dy)))
        projx = x1 + t*dx
        projy = y1 + t*dy
        return math.hypot(x0-projx, y0-projy)

    def pick_polygon(self, pos, tol=5):
        x, y = pos
        for polygon in reversed(self.all_polygons):
            if polygon.image_index != self.index:
                continue
            for point in polygon.points:
                if math.hypot(point[0]-x, point[1]-y) < tol:
                    return polygon
        return None

    def pick_polygon_point(self, pos, polygon, tol=5):
        x, y = pos
        for i, point in enumerate(polygon.points):
            if math.hypot(point[0]-x, point[1]-y) < tol:
                return i
        return None

    def on_drag(self, event):
        coords = self.image_coord_from_canvas(event.x, event.y)
        if coords:
            if self.selected_segment is not None and self.drag_point_index is not None:
                self.selected_segment.points[self.drag_point_index] = coords
                self.redraw()
            elif self.selected_angle is not None and self.drag_point_index is not None:
                if self.drag_point_index == 0:
                    self.selected_angle.vertex_point = coords
                elif self.drag_point_index == 1:
                    self.selected_angle.point1 = coords
                elif self.drag_point_index == 2:
                    self.selected_angle.point2 = coords
                self.redraw()
            elif self.selected_circle is not None and self.drag_point_index is not None:
                if self.drag_point_index == 0:
                    self.selected_circle.center = coords
                elif self.drag_point_index == 1:
                    self.selected_circle.radius_point = coords
                self.redraw()
            elif self.selected_rectangle is not None and self.drag_point_index is not None:
                self.selected_rectangle.points[self.drag_point_index] = coords
                self.redraw()
            elif self.selected_point_to_line is not None and self.drag_point_index is not None:
                if self.drag_point_index == 0:
                    self.selected_point_to_line.point = coords
                elif self.drag_point_index == 1:
                    self.selected_point_to_line.line_start = coords
                elif self.drag_point_index == 2:
                    self.selected_point_to_line.line_end = coords
                self.redraw()
            elif self.selected_polygon is not None and self.drag_point_index is not None:
                self.selected_polygon.points[self.drag_point_index] = coords
                self.redraw()

    def on_release(self, event):
        if self.drag_point_index is not None:
            self.save_state()
            self._save_current_annotations()
        self.drag_point_index = None

    def export_lengths(self):
        if not self.all_segments:
            messagebox.showinfo('提示', '没有线段可导出')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if not path:
            return
        n = export_lengths_to_csv(self, path)
        messagebox.showinfo('导出成功', f'已导出 {n} 个线段到 {path}')

    def batch_export(self):
        if not self.image_paths:
            messagebox.showinfo('提示', '请先打开图片')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if not path:
            return
        n = batch_export_all(self, path)
        messagebox.showinfo('批量导出成功', f'已导出所有测量数据到 {path}')

    def save_project(self):
        if not self.image_paths:
            messagebox.showinfo('提示', '请先打开图片')
            return
        path = filedialog.asksaveasfilename(defaultextension='.project.json', filetypes=[('Project', '*.project.json')])
        if not path:
            return
        project_data = build_project_data(self)
        if FileHandler.save_project(path, project_data):
            messagebox.showinfo('保存成功', f'项目已保存到 {path}')
        else:
            messagebox.showerror('保存失败', '无法保存项目文件')

    def load_project(self):
        path = filedialog.askopenfilename(filetypes=[('Project', '*.project.json')])
        if not path:
            return
        project_data = FileHandler.load_project(path)
        if not project_data:
            messagebox.showerror('加载失败', '无法加载项目文件')
            return
        load_project_data(self, project_data)
        if self.image_paths:
            self.load_image()
        messagebox.showinfo('加载成功', f'项目已加载，包含 {len(self.image_paths)} 张图片')

    def save_state(self):
        self.history.push(snapshot_from_app(self))

    def undo(self):
        state = self.history.undo()
        if state is not None:
            apply_state(self, state)
            self.redraw()
            self.update_status()

    def redo(self):
        state = self.history.redo()
        if state is not None:
            apply_state(self, state)
            self.redraw()
            self.update_status()

    def restore_state(self, state):
        apply_state(self, state)

    def zoom(self, factor):
        new_scale = self.scale_factor * factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        self.scale_factor = new_scale
        if hasattr(self, 'scale_input'):
            self.scale_input.update_scale(self.scale_factor)
        self.redraw()

    def reset_scale(self):
        self.scale_factor = 1.0
        if hasattr(self, 'scale_input'):
            self.scale_input.update_scale(self.scale_factor)
        self.redraw()

    def set_scale(self, scale):
        self.scale_factor = max(self.min_scale, min(self.max_scale, scale))
        if hasattr(self, 'scale_input'):
            self.scale_input.update_scale(self.scale_factor)
        self.redraw()

    def convert_length(self, pixels, target_unit=None):
        if target_unit is None:
            target_unit = self.current_unit
        return pixels * self.unit_conversion[target_unit]

    def set_unit(self, unit):
        if unit in self.units:
            self.current_unit = unit
            self.unit_var.set(unit)
            self.redraw()
            self.update_status()

    def _on_unit_change(self, value):
        self.set_unit(value)

    def get_unit_display(self, length_pixels):
        converted = self.convert_length(length_pixels)
        return f"{converted:.2f}{self.current_unit}"

    def calculate_angle(self, vertex, point1, point2):
        v1 = (point1[0] - vertex[0], point1[1] - vertex[1])
        v2 = (point2[0] - vertex[0], point2[1] - vertex[1])
        
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        cos_angle = dot / (mag1 * mag2)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        
        angle = math.degrees(math.acos(cos_angle))
        return angle

    def enable_length_mode(self):
        tools_switch_mode(self, Tool.LENGTH, self.measure_btn, tools_get_active_label(Tool.LENGTH))
        self.redraw()

    def enable_angle_mode(self):
        tools_switch_mode(self, Tool.ANGLE, self.measure_btn, tools_get_active_label(Tool.ANGLE))
        self.redraw()

    def enable_circle_mode(self):
        tools_switch_mode(self, Tool.CIRCLE, self.measure_btn, tools_get_active_label(Tool.CIRCLE))
        self.redraw()

    def enable_rectangle_mode(self):
        tools_switch_mode(self, Tool.RECTANGLE, self.measure_btn, tools_get_active_label(Tool.RECTANGLE))
        self.redraw()

    def enable_point_to_line_mode(self):
        tools_switch_mode(self, Tool.POINT_TO_LINE, self.measure_btn, tools_get_active_label(Tool.POINT_TO_LINE))
        self.redraw()

    def enable_polygon_mode(self):
        tools_switch_mode(self, Tool.POLYGON, self.measure_btn, tools_get_active_label(Tool.POLYGON))
        self.redraw()

    def toggle_angle_mode(self):
        self.angle_mode = not self.angle_mode
        self.angle_points = []
        self.redraw()

    def add_angle_point(self, point):
        tools_add_point(self, Tool.ANGLE, point)
        self.redraw()

    def add_circle_point(self, point):
        tools_add_point(self, Tool.CIRCLE, point)
        self.redraw()

    def add_rectangle_point(self, point):
        tools_add_point(self, Tool.RECTANGLE, point)
        self.redraw()

    def add_point_to_line_point(self, point):
        tools_add_point(self, Tool.POINT_TO_LINE, point)
        self.redraw()

    def add_polygon_point(self, point):
        tools_add_point(self, Tool.POLYGON, point)
        self.redraw()

    def finish_polygon(self):
        seg = tools_finish(self, Tool.POLYGON, self.index)
        if seg is not None:
            self._add_annotation(seg)
            self.redraw()

    def cancel_polygon(self):
        self.polygon_points = []
        self.redraw()
