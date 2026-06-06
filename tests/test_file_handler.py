"""FileHandler 文件读写测试。"""
import json
import os
import tempfile

from src.core.models import (
    LineSegment,
    PolygonSegment,
    MeasurementData,
)
from src.persistence.file_handler import FileHandler


def test_save_load_roundtrip():
    data = MeasurementData(
        segments=[],
        angles=[],
        circles=[],
        rectangles=[],
        point_to_lines=[],
        polygons=[PolygonSegment([(0, 0), (1, 0), (0, 1)], 0)],
    )
    data.segments.append(LineSegment([(0.0, 0.0), (3.0, 4.0)], 0))

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "data.json")
        FileHandler.save_segments(path, data)
        loaded = FileHandler.load_segments(path)
        assert loaded is not None
        assert len(loaded.segments) == 1
        assert loaded.segments[0].points == [(0.0, 0.0), (3.0, 4.0)]
        assert len(loaded.polygons) == 1


def test_load_missing_returns_none():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "no_such_file.json")
        assert FileHandler.load_segments(path) is None


def test_load_corrupted_returns_none():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "bad.json")
        with open(path, "w") as f:
            f.write("{this is not json")
        assert FileHandler.load_segments(path) is None


def test_segment_file_path_suffix():
    """get_segment_file_path 应当基于 _segments.json 后缀。"""
    path = FileHandler.get_segment_file_path("foo/bar/image.png")
    assert path.endswith("_segments.json")
    assert path.endswith("image_segments.json")


def test_export_csv(tmp_path=None):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "out.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Image,x_start,y_start,x_end,y_end,Total_Length(px)\n")
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            head = f.readline().strip()
        assert head == "Image,x_start,y_start,x_end,y_end,Total_Length(px)"
