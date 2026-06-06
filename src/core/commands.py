"""文件 I/O、CSV 导出、项目保存/加载。"""
import csv
import math
import os
from typing import Dict, List

from src.core.constants import SAVE_SUFFIX
from src.core.models import (
    AngleSegment,
    CircleSegment,
    LineSegment,
    PointToLineSegment,
    PolygonSegment,
    RectangleSegment,
)


def _safe_image_name(app, image_index) -> str:
    """根据 image_index 找图名，越界时回退占位。"""
    try:
        return os.path.basename(app.image_paths[image_index])
    except (IndexError, TypeError):
        return f"image_{image_index}"


def export_lengths_to_csv(app, file_path: str) -> int:
    """导出当前线段到 CSV，返回写入行数（不含表头）。"""
    rows: List[List] = []
    for seg in app.all_segments:
        pts = seg.points
        if len(pts) < 2:
            continue
        length = sum(
            math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
            for i in range(len(pts) - 1)
        )
        start, end = pts[0], pts[-1]
        rows.append([
            _safe_image_name(app, seg.image_index),
            start[0], start[1], end[0], end[1], f"{length:.2f}",
        ])

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Image", "x_start", "y_start", "x_end", "y_end", "Total_Length(px)"])
        writer.writerows(rows)
    return len(rows)


def batch_export_all(app, file_path: str) -> int:
    """批量导出所有图片的线段。"""
    rows: List[List] = []
    image_paths = getattr(app, "image_paths", []) or []
    for img_idx in range(len(image_paths)):
        for seg in app.all_segments:
            if seg.image_index != img_idx:
                continue
            pts = seg.points
            if len(pts) < 2:
                continue
            length = sum(
                math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
                for i in range(len(pts) - 1)
            )
            start, end = pts[0], pts[-1]
            rows.append([
                _safe_image_name(app, img_idx),
                start[0], start[1], end[0], end[1], f"{length:.2f}",
            ])

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Image", "x_start", "y_start", "x_end", "y_end", "Total_Length(px)"])
        writer.writerows(rows)
    return len(rows)


def build_project_data(app) -> Dict:
    return {
        "image_paths": list(app.image_paths),
        "current_index": app.index,
        "segments": [seg.to_dict() for seg in app.all_segments],
        "angles": [a.to_dict() for a in app.all_angles],
        "circles": [c.to_dict() for c in app.all_circles],
        "rectangles": [r.to_dict() for r in app.all_rectangles],
        "point_to_lines": [p.to_dict() for p in app.all_point_to_lines],
        "current_unit": app.current_unit,
    }


def load_project_data(app, project_data: Dict) -> None:
    app.image_paths = list(project_data.get("image_paths", []))
    app.index = project_data.get("current_index", 0)
    app.all_segments = [LineSegment.from_dict(s) for s in project_data.get("segments", [])]
    app.all_angles = [AngleSegment.from_dict(a) for a in project_data.get("angles", [])]
    app.all_circles = [CircleSegment.from_dict(c) for c in project_data.get("circles", [])]
    app.all_rectangles = [RectangleSegment.from_dict(r) for r in project_data.get("rectangles", [])]
    app.all_point_to_lines = [PointToLineSegment.from_dict(p) for p in project_data.get("point_to_lines", [])]
    app.current_unit = project_data.get("current_unit", "px")
    if hasattr(app, "unit_var") and app.unit_var is not None:
        try:
            app.unit_var.set(app.current_unit)
        except Exception:
            pass


def save_annotated_image(app, target_path: str = None) -> str:
    """将当前图（含标注）保存到 *_measured.ext。返回实际保存路径。"""
    from src.core.drawing import draw_annotations_to_orig
    if not app.orig_image:
        raise ValueError("orig_image is None")
    img = draw_annotations_to_orig(app.orig_image, app)
    if target_path is None:
        path = app.image_paths[app.index]
        base, ext = os.path.splitext(path)
        target_path = base + SAVE_SUFFIX + ext
    img.save(target_path)
    return target_path
