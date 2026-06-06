"""拾取/拖拽统一接口。"""
import math
from typing import Callable, Dict, Optional

from src.core.constants import PICK_TOLERANCE


def _dist_point_to_segment(p, a, b) -> float:
    x0, y0 = p
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x0 - x1, y0 - y1)
    t = max(0.0, min(1.0, ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)))
    projx = x1 + t * dx
    projy = y1 + t * dy
    return math.hypot(x0 - projx, y0 - projy)


def _dist_points(p, q) -> float:
    return math.hypot(p[0] - q[0], p[1] - q[1])


def pick_segment(segments, image_index, pos, tol=PICK_TOLERANCE):
    for seg in reversed(segments):
        if seg.image_index != image_index:
            continue
        for i in range(len(seg.points) - 1):
            if _dist_point_to_segment(pos, seg.points[i], seg.points[i + 1]) < tol:
                return seg
    return None


def pick_point(seg, pos, tol=PICK_TOLERANCE) -> Optional[int]:
    for i, (px, py) in enumerate(seg.points):
        if _dist_points(pos, (px, py)) < tol:
            return i
    return None


def pick_angle(angles, image_index, pos, tol=PICK_TOLERANCE):
    for angle in reversed(angles):
        if angle.image_index != image_index:
            continue
        for q in (angle.vertex_point, angle.point1, angle.point2):
            if _dist_points(pos, q) < tol:
                return angle
    return None


def pick_angle_point(angle, pos, tol=PICK_TOLERANCE) -> Optional[int]:
    for idx, q in enumerate((angle.vertex_point, angle.point1, angle.point2)):
        if _dist_points(pos, q) < tol:
            return idx
    return None


def pick_circle(circles, image_index, pos, tol=PICK_TOLERANCE):
    for circle in reversed(circles):
        if circle.image_index != image_index:
            continue
        for q in (circle.center, circle.radius_point):
            if _dist_points(pos, q) < tol:
                return circle
    return None


def pick_circle_point(circle, pos, tol=PICK_TOLERANCE) -> Optional[int]:
    for idx, q in enumerate((circle.center, circle.radius_point)):
        if _dist_points(pos, q) < tol:
            return idx
    return None


def pick_rectangle(rectangles, image_index, pos, tol=PICK_TOLERANCE):
    for rect in reversed(rectangles):
        if rect.image_index != image_index:
            continue
        for p in rect.points:
            if _dist_points(pos, p) < tol:
                return rect
    return None


def pick_rectangle_point(rect, pos, tol=PICK_TOLERANCE) -> Optional[int]:
    for i, p in enumerate(rect.points):
        if _dist_points(pos, p) < tol:
            return i
    return None


def pick_point_to_line(ptls, image_index, pos, tol=PICK_TOLERANCE):
    for ptl in reversed(ptls):
        if ptl.image_index != image_index:
            continue
        for q in (ptl.point, ptl.line_start, ptl.line_end):
            if _dist_points(pos, q) < tol:
                return ptl
    return None


def pick_point_to_line_point(ptl, pos, tol=PICK_TOLERANCE) -> Optional[int]:
    for idx, q in enumerate((ptl.point, ptl.line_start, ptl.line_end)):
        if _dist_points(pos, q) < tol:
            return idx
    return None


def pick_polygon(polygons, image_index, pos, tol=PICK_TOLERANCE):
    for polygon in reversed(polygons):
        if polygon.image_index != image_index:
            continue
        for p in polygon.points:
            if _dist_points(pos, p) < tol:
                return polygon
    return None


def pick_polygon_point(polygon, pos, tol=PICK_TOLERANCE) -> Optional[int]:
    for i, p in enumerate(polygon.points):
        if _dist_points(pos, p) < tol:
            return i
    return None


def clamp_to_image(coords, image_size):
    """限制坐标在图片范围内。"""
    if coords is None or image_size is None:
        return coords
    iw, ih = image_size
    x, y = coords
    return (max(0.0, min(iw - 1, x)), max(0.0, min(ih - 1, y)))


PICKERS: Dict[str, Callable] = {
    "angle": pick_angle,
    "circle": pick_circle,
    "rectangle": pick_rectangle,
    "point_to_line": pick_point_to_line,
    "polygon": pick_polygon,
}


POINT_PICKERS: Dict[str, Callable] = {
    "angle": pick_angle_point,
    "circle": pick_circle_point,
    "rectangle": pick_rectangle_point,
    "point_to_line": pick_point_to_line_point,
    "polygon": pick_polygon_point,
}
