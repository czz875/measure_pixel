"""CircleSegment 旧字段兼容测试。"""
from src.core.models import CircleSegment


def test_from_new_field():
    data = {"center": [10, 20], "radius_point": [30, 40], "image_index": 0}
    c = CircleSegment.from_dict(data)
    assert c.center == (10, 20)
    assert c.radius_point == (30, 40)
    assert c.image_index == 0


def test_from_legacy_field():
    """旧项目文件使用 point_on_circle 字段，应仍能加载。"""
    data = {"center": [5, 6], "point_on_circle": [7, 8], "image_index": 1}
    c = CircleSegment.from_dict(data)
    assert c.center == (5, 6)
    assert c.radius_point == (7, 8)
    assert c.image_index == 1


def test_to_dict_uses_new_field():
    c = CircleSegment(center=(0, 0), radius_point=(1, 1), image_index=0)
    d = c.to_dict()
    assert "radius_point" in d
    assert "point_on_circle" not in d
    assert d["radius_point"] == [1.0, 1.0]
    assert d["image_index"] == 0
