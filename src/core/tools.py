"""6 种测量模式的切换与点添加。"""
from enum import Enum

from src.core.models import (
    AngleSegment,
    CircleSegment,
    LineSegment,
    PointToLineSegment,
    PolygonSegment,
    RectangleSegment,
)


class Tool(Enum):
    NONE = "none"
    LENGTH = "length"
    ANGLE = "angle"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    POINT_TO_LINE = "point_to_line"
    POLYGON = "polygon"


_MODE_TO_ATTR = {
    Tool.LENGTH: "current_points",
    Tool.ANGLE: "angle_points",
    Tool.CIRCLE: "circle_points",
    Tool.RECTANGLE: "rectangle_points",
    Tool.POINT_TO_LINE: "point_to_line_points",
    Tool.POLYGON: "polygon_points",
}


_MODE_TO_LIMIT = {
    Tool.LENGTH: None,
    Tool.ANGLE: 3,
    Tool.CIRCLE: 2,
    Tool.RECTANGLE: 2,
    Tool.POINT_TO_LINE: 3,
    Tool.POLYGON: None,
}


_MODE_FLAGS = ("angle_mode", "circle_mode", "rectangle_mode", "point_to_line_mode", "polygon_mode")


def switch_mode(app, tool: Tool, measure_btn=None, active_label: str = None) -> None:
    """切换工具模式，清空其它模式与临时点。"""
    for attr in _MODE_FLAGS:
        setattr(app, attr, False)
    if tool == Tool.LENGTH:
        app.angle_points = []
    elif tool == Tool.ANGLE:
        app.angle_mode = True
        app.angle_points = []
    elif tool == Tool.CIRCLE:
        app.circle_mode = True
        app.circle_points = []
    elif tool == Tool.RECTANGLE:
        app.rectangle_mode = True
        app.rectangle_points = []
    elif tool == Tool.POINT_TO_LINE:
        app.point_to_line_mode = True
        app.point_to_line_points = []
    elif tool == Tool.POLYGON:
        app.polygon_mode = True
        app.polygon_points = []
    if measure_btn is not None and active_label is not None:
        try:
            measure_btn.set_active_menu_item(active_label)
        except Exception:
            pass


def add_point(app, tool: Tool, point) -> None:
    """向当前模式添加一个点。"""
    attr = _MODE_TO_ATTR[tool]
    limit = _MODE_TO_LIMIT[tool]
    pts = getattr(app, attr)
    if limit is None or len(pts) < limit:
        pts.append(point)


def pop_point(app, tool: Tool):
    """弹出当前模式的最后一个点。"""
    attr = _MODE_TO_ATTR[tool]
    pts = getattr(app, attr)
    if pts:
        pts.pop()


def finish(app, tool: Tool, image_index: int):
    """按当前模式完成一次标注，返回构造的 segment 或 None。"""
    if tool == Tool.LENGTH and len(app.current_points) >= 2:
        seg = LineSegment(app.current_points.copy(), image_index)
        app.current_points = []
        return seg
    if tool == Tool.ANGLE and len(app.angle_points) == 3:
        seg = AngleSegment(app.angle_points[1], app.angle_points[0], app.angle_points[2], image_index)
        app.angle_points = []
        return seg
    if tool == Tool.CIRCLE and len(app.circle_points) == 2:
        seg = CircleSegment(app.circle_points[0], app.circle_points[1], image_index)
        app.circle_points = []
        return seg
    if tool == Tool.RECTANGLE and len(app.rectangle_points) == 2:
        seg = RectangleSegment(app.rectangle_points, image_index)
        app.rectangle_points = []
        return seg
    if tool == Tool.POINT_TO_LINE and len(app.point_to_line_points) == 3:
        seg = PointToLineSegment(
            app.point_to_line_points[0],
            app.point_to_line_points[1],
            app.point_to_line_points[2],
            image_index,
        )
        app.point_to_line_points = []
        return seg
    if tool == Tool.POLYGON and len(app.polygon_points) >= 3:
        seg = PolygonSegment(app.polygon_points.copy(), image_index)
        app.polygon_points = []
        return seg
    return None


def current_mode(app) -> Tool:
    """探测 app 当前所处的工具模式。"""
    if app.angle_mode:
        return Tool.ANGLE
    if app.circle_mode:
        return Tool.CIRCLE
    if app.rectangle_mode:
        return Tool.RECTANGLE
    if app.point_to_line_mode:
        return Tool.POINT_TO_LINE
    if app.polygon_mode:
        return Tool.POLYGON
    return Tool.LENGTH


def get_active_label(tool: Tool) -> str:
    return {
        Tool.LENGTH: "测量距离",
        Tool.ANGLE: "测量角度",
        Tool.CIRCLE: "测量圆形",
        Tool.RECTANGLE: "测量矩形",
        Tool.POINT_TO_LINE: "点到线距离",
        Tool.POLYGON: "多边形测面积",
    }.get(tool, "")
