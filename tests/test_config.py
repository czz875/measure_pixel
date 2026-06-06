"""Config 配置相关测试。"""
import os

from src.config.settings import Config


def test_base_dir_points_to_project_root():
    assert Config.BASE_DIR.endswith("tools")
    assert os.path.isabs(Config.BASE_DIR)


def test_units_consistent():
    expected = ("px", "mm", "cm", "in")
    assert Config.UNITS == expected
    assert Config.MEASUREMENT["default_unit"] in expected


def test_get_units_returns_list():
    units = Config.get_units()
    assert isinstance(units, list)
    assert units == ["px", "mm", "cm", "in"]


def test_image_scale_range():
    assert Config.IMAGE["min_scale"] < Config.IMAGE["max_scale"]
    assert Config.IMAGE["default_scale"] >= Config.IMAGE["min_scale"]
    assert Config.IMAGE["default_scale"] <= Config.IMAGE["max_scale"]
