"""7 类标注的 PIL 绘制。"""
import math
from typing import Callable

from PIL import Image, ImageDraw

from src.core.font_loader import get_font
from src.core.constants import (
    COLOR_LINE_DASH,
    COLOR_LINE_POINT,
    COLOR_CURRENT_POINT,
    COLOR_ANGLE_DEFAULT,
    COLOR_ANGLE_SELECTED,
    COLOR_ANGLE_VERTEX_HINT,
    COLOR_CIRCLE_DEFAULT,
    COLOR_CIRCLE_SELECTED,
    COLOR_RECT_DEFAULT,
    COLOR_RECT_SELECTED,
    COLOR_PTL_DEFAULT,
    COLOR_PTL_SELECTED,
    COLOR_POLYGON_DEFAULT,
    COLOR_POLYGON_SELECTED,
    FONT_SIZE_TEXT,
    FONT_SIZE_LABEL_BASE,
    FONT_SIZE_EXPORT,
)


def _scale(point, disp_w, disp_h, orig_w, orig_h):
    x, y = point
    return (int(x * disp_w / orig_w), int(y * disp_h / orig_h))


def _draw_dashed_line(draw, p1, p2, fill=COLOR_LINE_DASH, width=2, dash_size=10):
    length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    if length <= 0:
        return
    num_dashes = max(int(length / dash_size), 1)
    for j in range(num_dashes):
        t1 = j / num_dashes
        t2 = (j + 0.5) / num_dashes
        draw.line(
            [
                (
                    p1[0] + (p2[0] - p1[0]) * t1,
                    p1[1] + (p2[1] - p1[1]) * t1,
                ),
                (
                    p1[0] + (p2[0] - p1[0]) * t2,
                    p1[1] + (p2[1] - p1[1]) * t2,
                ),
            ],
            fill=fill,
            width=width,
        )


def _draw_point(draw, p, scale_factor, color, base=4):
    r = max(base, int(base * scale_factor))
    draw.ellipse(
        (p[0] - r, p[1] - r, p[0] + r, p[1] + r),
        outline=color,
        width=2,
    )


def _selected_color(item, selected, default_color, selected_color):
    return selected_color if item == selected else default_color


def _selected_width(item, selected):
    return 3 if item == selected else 2


def draw_segments(draw, segments, image_index, disp_w, disp_h, orig_w, orig_h,
                  scale_factor, selected, get_unit_display):
    font = get_font(FONT_SIZE_TEXT)
    for seg in segments:
        if seg.image_index != image_index:
            continue
        scaled = [_scale(p, disp_w, disp_h, orig_w, orig_h) for p in seg.points]
        for i in range(len(scaled) - 1):
            _draw_dashed_line(draw, scaled[i], scaled[i + 1])
            x1, y1 = seg.points[i]
            x2, y2 = seg.points[i + 1]
            length = math.hypot(x2 - x1, y2 - y1)
            midx = int((x1 + x2) / 2 * disp_w / orig_w)
            midy = int((y1 + y2) / 2 * disp_h / orig_h)
            draw.text(
                (midx + 5, midy + 5),
                get_unit_display(length),
                font=font,
                fill=COLOR_LINE_DASH,
            )
        for p in scaled:
            _draw_point(draw, p, scale_factor, COLOR_LINE_POINT, base=4)


def draw_current_segment(draw, current_points, disp_w, disp_h, orig_w, orig_h, scale_factor):
    if not current_points:
        return
    scaled = [_scale(p, disp_w, disp_h, orig_w, orig_h) for p in current_points]
    for i in range(len(scaled) - 1):
        draw.line([scaled[i], scaled[i + 1]], width=2, fill=COLOR_CURRENT_POINT)
    for p in scaled:
        _draw_point(draw, p, scale_factor, COLOR_CURRENT_POINT, base=3)


def draw_angles(draw, angles, image_index, disp_w, disp_h, orig_w, orig_h,
                scale_factor, selected, calculate_angle):
    font = get_font(max(FONT_SIZE_LABEL_BASE, int(FONT_SIZE_LABEL_BASE * scale_factor)))
    for angle in angles:
        if angle.image_index != image_index:
            continue
        vertex = _scale(angle.vertex_point, disp_w, disp_h, orig_w, orig_h)
        p1 = _scale(angle.point1, disp_w, disp_h, orig_w, orig_h)
        p2 = _scale(angle.point2, disp_w, disp_h, orig_w, orig_h)
        line_color = _selected_color(angle, selected, COLOR_ANGLE_DEFAULT, COLOR_ANGLE_SELECTED)
        line_width = _selected_width(angle, selected)
        draw.line([vertex, p1], fill=line_color, width=line_width)
        draw.line([vertex, p2], fill=line_color, width=line_width)
        r = max(4, int(4 * scale_factor))
        draw.ellipse(
            (vertex[0] - r, vertex[1] - r, vertex[0] + r, vertex[1] + r),
            outline=line_color,
            width=line_width,
        )
        angle_value = calculate_angle(angle.vertex_point, angle.point1, angle.point2)
        draw.text(
            (vertex[0] + 10, vertex[1] - 20),
            f"{angle_value:.1f}°",
            font=font,
            fill=line_color,
        )


def draw_angle_preview(draw, angle_points, disp_w, disp_h, orig_w, orig_h, scale_factor):
    if not angle_points:
        return
    scaled = [_scale(p, disp_w, disp_h, orig_w, orig_h) for p in angle_points]
    for i, p in enumerate(scaled):
        color = COLOR_ANGLE_VERTEX_HINT if i == 0 else COLOR_ANGLE_SELECTED
        _draw_point(draw, p, scale_factor, color, base=4)
        if i > 0:
            draw.line([scaled[0], p], fill=COLOR_ANGLE_VERTEX_HINT, width=2)


def draw_circles(draw, circles, image_index, disp_w, disp_h, orig_w, orig_h,
                 scale_factor, selected, get_unit_display):
    font = get_font(max(FONT_SIZE_LABEL_BASE, int(FONT_SIZE_LABEL_BASE * scale_factor)))
    for circle in circles:
        if circle.image_index != image_index:
            continue
        center = _scale(circle.center, disp_w, disp_h, orig_w, orig_h)
        rp = _scale(circle.radius_point, disp_w, disp_h, orig_w, orig_h)
        radius = int(math.hypot(rp[0] - center[0], rp[1] - center[1]))
        line_color = _selected_color(circle, selected, COLOR_CIRCLE_DEFAULT, COLOR_CIRCLE_SELECTED)
        line_width = _selected_width(circle, selected)
        draw.ellipse(
            (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
            outline=line_color,
            width=line_width,
        )
        draw.line([center, rp], fill=line_color, width=line_width)
        r = max(4, int(4 * scale_factor))
        draw.ellipse(
            (center[0] - r, center[1] - r, center[0] + r, center[1] + r),
            outline=line_color,
            width=line_width,
        )
        draw.text(
            (center[0] + radius + 5, center[1] - radius),
            f"R:{get_unit_display(circle.radius)}",
            font=font,
            fill=line_color,
        )


def draw_circle_preview(draw, circle_points, disp_w, disp_h, orig_w, orig_h, scale_factor):
    if not circle_points:
        return
    scaled = [_scale(p, disp_w, disp_h, orig_w, orig_h) for p in circle_points]
    for i, p in enumerate(scaled):
        color = COLOR_CIRCLE_SELECTED if i == 0 else COLOR_CIRCLE_DEFAULT
        _draw_point(draw, p, scale_factor, color, base=4)
        if len(scaled) == 2:
            center = scaled[0]
            rp = scaled[1]
            radius = int(math.hypot(rp[0] - center[0], rp[1] - center[1]))
            draw.ellipse(
                (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
                outline=COLOR_CIRCLE_DEFAULT,
                width=2,
            )


def draw_rectangles(draw, rectangles, image_index, disp_w, disp_h, orig_w, orig_h,
                    scale_factor, selected, get_unit_display):
    font = get_font(max(FONT_SIZE_LABEL_BASE, int(FONT_SIZE_LABEL_BASE * scale_factor)))
    for rect in rectangles:
        if rect.image_index != image_index:
            continue
        p1 = _scale(rect.points[0], disp_w, disp_h, orig_w, orig_h)
        p2 = _scale(rect.points[1], disp_w, disp_h, orig_w, orig_h)
        x0, x1 = min(p1[0], p2[0]), max(p1[0], p2[0])
        y0, y1 = min(p1[1], p2[1]), max(p1[1], p2[1])
        line_color = _selected_color(rect, selected, COLOR_RECT_DEFAULT, COLOR_RECT_SELECTED)
        line_width = _selected_width(rect, selected)
        draw.rectangle([x0, y0, x1, y1], outline=line_color, width=line_width)
        r = max(4, int(4 * scale_factor))
        for p in [p1, p2]:
            draw.ellipse(
                (p[0] - r, p[1] - r, p[0] + r, p[1] + r),
                outline=line_color,
                width=line_width,
            )
        draw.text(
            (x0 + 5, y0 - 20),
            f"{get_unit_display(rect.width)}x{get_unit_display(rect.height)}",
            font=font,
            fill=line_color,
        )


def draw_rectangle_preview(draw, rectangle_points, disp_w, disp_h, orig_w, orig_h, scale_factor):
    if not rectangle_points:
        return
    scaled = [_scale(p, disp_w, disp_h, orig_w, orig_h) for p in rectangle_points]
    for i, p in enumerate(scaled):
        color = COLOR_RECT_SELECTED if i == 0 else COLOR_RECT_DEFAULT
        _draw_point(draw, p, scale_factor, color, base=4)
        if len(scaled) == 2:
            x0, x1 = min(scaled[0][0], scaled[1][0]), max(scaled[0][0], scaled[1][0])
            y0, y1 = min(scaled[0][1], scaled[1][1]), max(scaled[0][1], scaled[1][1])
            draw.rectangle([x0, y0, x1, y1], outline=COLOR_RECT_DEFAULT, width=2)


def draw_point_to_lines(draw, ptls, image_index, disp_w, disp_h, orig_w, orig_h,
                        scale_factor, selected, get_unit_display):
    font = get_font(max(FONT_SIZE_LABEL_BASE, int(FONT_SIZE_LABEL_BASE * scale_factor)))
    for ptl in ptls:
        if ptl.image_index != image_index:
            continue
        point = _scale(ptl.point, disp_w, disp_h, orig_w, orig_h)
        ls = _scale(ptl.line_start, disp_w, disp_h, orig_w, orig_h)
        le = _scale(ptl.line_end, disp_w, disp_h, orig_w, orig_h)
        line_color = _selected_color(ptl, selected, COLOR_PTL_DEFAULT, COLOR_PTL_SELECTED)
        line_width = _selected_width(ptl, selected)
        draw.line([ls, le], fill=line_color, width=line_width)
        r = max(4, int(4 * scale_factor))
        draw.ellipse(
            (point[0] - r, point[1] - r, point[0] + r, point[1] + r),
            outline=line_color,
            width=line_width,
        )
        draw.text(
            (point[0] + 10, point[1] - 20),
            f"d:{get_unit_display(ptl.distance)}",
            font=font,
            fill=line_color,
        )


def draw_ptl_preview(draw, ptl_points, disp_w, disp_h, orig_w, orig_h, scale_factor):
    if not ptl_points:
        return
    scaled = [_scale(p, disp_w, disp_h, orig_w, orig_h) for p in ptl_points]
    for i, p in enumerate(scaled):
        color = COLOR_PTL_SELECTED if i == 0 else COLOR_PTL_DEFAULT
        _draw_point(draw, p, scale_factor, color, base=4)
        if len(scaled) >= 3:
            draw.line([scaled[1], scaled[2]], fill=COLOR_PTL_DEFAULT, width=2)


def draw_polygons(draw, polygons, image_index, disp_w, disp_h, orig_w, orig_h,
                  scale_factor, selected, get_unit_display):
    font = get_font(max(FONT_SIZE_LABEL_BASE, int(FONT_SIZE_LABEL_BASE * scale_factor)))
    for polygon in polygons:
        if polygon.image_index != image_index:
            continue
        scaled = [_scale(p, disp_w, disp_h, orig_w, orig_h) for p in polygon.points]
        line_color = _selected_color(polygon, selected, COLOR_POLYGON_DEFAULT, COLOR_POLYGON_SELECTED)
        line_width = _selected_width(polygon, selected)
        if len(scaled) >= 3:
            draw.polygon(scaled, outline=line_color, width=line_width)
        r = max(4, int(4 * scale_factor))
        for p in scaled:
            draw.ellipse(
                (p[0] - r, p[1] - r, p[0] + r, p[1] + r),
                outline=line_color,
                width=line_width,
            )
        centroid_x = sum(p[0] for p in scaled) // len(scaled)
        centroid_y = sum(p[1] for p in scaled) // len(scaled)
        draw.text(
            (centroid_x + 5, centroid_y - 20),
            f"A:{get_unit_display(polygon.area)}",
            font=font,
            fill=line_color,
        )


def draw_polygon_preview(draw, polygon_points, disp_w, disp_h, orig_w, orig_h, scale_factor):
    if not polygon_points:
        return
    scaled = [_scale(p, disp_w, disp_h, orig_w, orig_h) for p in polygon_points]
    for i, p in enumerate(scaled):
        _draw_point(draw, p, scale_factor, COLOR_POLYGON_SELECTED, base=4)
        if i > 0:
            draw.line([scaled[i - 1], p], fill=COLOR_POLYGON_SELECTED, width=2)
        if len(scaled) >= 3:
            draw.line([scaled[-1], scaled[0]], fill=COLOR_POLYGON_SELECTED, width=2)


def compute_display_size(canvas, orig_image, scale_factor):
    """根据 canvas 与 orig_image 计算 display_size。"""
    cw, ch = canvas.winfo_width(), canvas.winfo_height()
    iw, ih = orig_image.size
    scale = min(cw / iw, ch / ih, 1.0) * scale_factor
    return (int(iw * scale), int(ih * scale))


def draw_annotations_on_image(
    orig_image: Image.Image,
    app,
    scale_factor: float,
    get_unit_display: Callable,
    calculate_angle: Callable,
) -> Image.Image:
    """在 orig_image 副本上叠加所有标注和预览，返回新图像。"""
    iw, ih = orig_image.size
    disp_w, disp_h = compute_display_size(app.canvas, orig_image, scale_factor)
    app.display_size = (disp_w, disp_h)
    disp = orig_image.resize((disp_w, disp_h), Image.LANCZOS)
    overlay = disp.copy()
    draw = ImageDraw.Draw(overlay)

    segs, angles, circles, rects, ptls, polygons = app._get_current_annotations()
    draw_segments(draw, segs, app.index, disp_w, disp_h, iw, ih, scale_factor, app.selected_segment, get_unit_display)
    draw_current_segment(draw, app.current_points, disp_w, disp_h, iw, ih, scale_factor)
    draw_angles(draw, angles, app.index, disp_w, disp_h, iw, ih, scale_factor, app.selected_angle, calculate_angle)
    draw_angle_preview(draw, app.angle_points, disp_w, disp_h, iw, ih, scale_factor)
    draw_circles(draw, circles, app.index, disp_w, disp_h, iw, ih, scale_factor, app.selected_circle, get_unit_display)
    draw_circle_preview(draw, app.circle_points, disp_w, disp_h, iw, ih, scale_factor)
    draw_rectangles(draw, rects, app.index, disp_w, disp_h, iw, ih, scale_factor, app.selected_rectangle, get_unit_display)
    draw_rectangle_preview(draw, app.rectangle_points, disp_w, disp_h, iw, ih, scale_factor)
    draw_point_to_lines(draw, ptls, app.index, disp_w, disp_h, iw, ih, scale_factor, app.selected_point_to_line, get_unit_display)
    draw_ptl_preview(draw, app.point_to_line_points, disp_w, disp_h, iw, ih, scale_factor)
    draw_polygons(draw, polygons, app.index, disp_w, disp_h, iw, ih, scale_factor, app.selected_polygon, get_unit_display)
    draw_polygon_preview(draw, app.polygon_points, disp_w, disp_h, iw, ih, scale_factor)

    return overlay


def draw_annotations_to_orig(orig_image: Image.Image, app) -> Image.Image:
    """在原图分辨率上叠加标注（用于导出）。"""
    img = orig_image.copy()
    draw = ImageDraw.Draw(img)
    font = get_font(FONT_SIZE_EXPORT)
    segs, angles, circles, rects, ptls, polygons = app._get_current_annotations()
    for seg in segs:
        for i in range(len(seg.points) - 1):
            p1, p2 = seg.points[i], seg.points[i + 1]
            _draw_dashed_line(draw, p1, p2, fill=COLOR_LINE_DASH, width=2, dash_size=20)
            midx = (p1[0] + p2[0]) / 2
            midy = (p1[1] + p2[1]) / 2
            length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            draw.text((midx + 5, midy), f"{length:.1f}px", fill=COLOR_LINE_DASH, font=font)
        r = 5
        for p in seg.points:
            draw.ellipse(
                (p[0] - r, p[1] - r, p[0] + r, p[1] + r),
                outline=COLOR_LINE_POINT,
                width=3,
            )
    return img
