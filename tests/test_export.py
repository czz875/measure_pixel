"""commands 导出与项目数据测试。"""
import os
import tempfile

from src.core.models import LineSegment
from src.core.commands import (
    _safe_image_name,
    build_project_data,
    load_project_data,
    export_lengths_to_csv,
)


class _FakeApp:
    def __init__(self, image_paths=None, segments=None):
        self.image_paths = image_paths or ["a.png", "b.png"]
        self.index = 0
        self.all_segments = segments or []
        self.all_angles = []
        self.all_circles = []
        self.all_rectangles = []
        self.all_point_to_lines = []
        self.current_unit = "px"
        self.unit_var = None


def test_safe_image_name_in_range():
    app = _FakeApp()
    assert _safe_image_name(app, 0) == "a.png"
    assert _safe_image_name(app, 1) == "b.png"


def test_safe_image_name_out_of_range():
    app = _FakeApp()
    assert _safe_image_name(app, 99) == "image_99"


def test_export_lengths_uses_each_segment_image_index():
    seg0 = LineSegment([(0.0, 0.0), (3.0, 4.0)], 0)
    seg1 = LineSegment([(10.0, 10.0), (13.0, 14.0)], 1)
    app = _FakeApp(segments=[seg0, seg1])
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "out.csv")
        n = export_lengths_to_csv(app, path)
        assert n == 2
        with open(path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines()]
    assert lines[0] == "Image,x_start,y_start,x_end,y_end,Total_Length(px)"
    assert "a.png,0.0,0.0,3.0,4.0,5.00" in lines[1]
    assert "b.png,10.0,10.0,13.0,14.0,5.00" in lines[2]


def test_build_and_load_project_data_roundtrip():
    app1 = _FakeApp(segments=[LineSegment([(1, 1), (4, 5)], 0)])
    data = build_project_data(app1)
    app2 = _FakeApp()
    load_project_data(app2, data)
    assert app2.image_paths == ["a.png", "b.png"]
    assert app2.index == 0
    assert len(app2.all_segments) == 1
    assert app2.all_segments[0].points == [(1, 1), (4, 5)]
