"""撤销/恢复栈，含多边形字段与上限。"""
from dataclasses import dataclass, field
from typing import List, Optional

from src.core.models import (
    LineSegment,
    AngleSegment,
    CircleSegment,
    RectangleSegment,
    PointToLineSegment,
    PolygonSegment,
)
from src.core.constants import MAX_HISTORY


@dataclass
class HistoryState:
    """一次撤销快照。"""
    segments: List[dict] = field(default_factory=list)
    angles: List[dict] = field(default_factory=list)
    circles: List[dict] = field(default_factory=list)
    rectangles: List[dict] = field(default_factory=list)
    point_to_lines: List[dict] = field(default_factory=list)
    polygons: List[dict] = field(default_factory=list)
    current_points: list = field(default_factory=list)
    angle_points: list = field(default_factory=list)
    circle_points: list = field(default_factory=list)
    rectangle_points: list = field(default_factory=list)
    point_to_line_points: list = field(default_factory=list)
    polygon_points: list = field(default_factory=list)


class History:
    """有限容量的撤销/恢复栈。"""

    def __init__(self, max_size: int = MAX_HISTORY):
        self._stack: List[HistoryState] = []
        self._index: int = -1
        self._max_size = max_size

    def push(self, state: HistoryState) -> None:
        """推入新状态，截断 redo 分支。"""
        self._stack = self._stack[: self._index + 1]
        self._stack.append(state)
        if len(self._stack) > self._max_size:
            overflow = len(self._stack) - self._max_size
            self._stack = self._stack[overflow:]
        self._index = len(self._stack) - 1

    def can_undo(self) -> bool:
        return self._index > 0

    def can_redo(self) -> bool:
        return 0 <= self._index < len(self._stack) - 1

    def undo(self) -> Optional[HistoryState]:
        if not self.can_undo():
            return None
        self._index -= 1
        return self._stack[self._index]

    def redo(self) -> Optional[HistoryState]:
        if not self.can_redo():
            return None
        self._index += 1
        return self._stack[self._index]

    def current(self) -> Optional[HistoryState]:
        if 0 <= self._index < len(self._stack):
            return self._stack[self._index]
        return None

    def __len__(self) -> int:
        return len(self._stack)


def snapshot_from_app(app) -> HistoryState:
    """从 app 实例构造一次状态快照。"""
    return HistoryState(
        segments=[s.to_dict() for s in app.all_segments],
        angles=[a.to_dict() for a in app.all_angles],
        circles=[c.to_dict() for c in app.all_circles],
        rectangles=[r.to_dict() for r in app.all_rectangles],
        point_to_lines=[p.to_dict() for p in app.all_point_to_lines],
        polygons=[p.to_dict() for p in app.all_polygons],
        current_points=list(app.current_points),
        angle_points=list(app.angle_points),
        circle_points=list(app.circle_points),
        rectangle_points=list(app.rectangle_points),
        point_to_line_points=list(app.point_to_line_points),
        polygon_points=list(app.polygon_points),
    )


def apply_state(app, state: HistoryState) -> None:
    """将状态应用到 app 实例。"""
    app.all_segments = [LineSegment.from_dict(s) for s in state.segments]
    app.all_angles = [AngleSegment.from_dict(a) for a in state.angles]
    app.all_circles = [CircleSegment.from_dict(c) for c in state.circles]
    app.all_rectangles = [RectangleSegment.from_dict(r) for r in state.rectangles]
    app.all_point_to_lines = [PointToLineSegment.from_dict(p) for p in state.point_to_lines]
    app.all_polygons = [PolygonSegment.from_dict(p) for p in state.polygons]
    app.current_points = list(state.current_points)
    app.angle_points = list(state.angle_points)
    app.circle_points = list(state.circle_points)
    app.rectangle_points = list(state.rectangle_points)
    app.point_to_line_points = list(state.point_to_line_points)
    app.polygon_points = list(state.polygon_points)
