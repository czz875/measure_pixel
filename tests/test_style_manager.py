"""StyleManager 样式管理测试。"""
import os

from src.ui.styles.manager import StyleManager


def test_default_colors_use_new_field_names():
    sm = StyleManager("nonexistent.json")
    assert sm.get_color("main_background") == "#FAFAFA"
    assert sm.get_color("toolbar") == "#F3F2F1"


def test_default_font():
    sm = StyleManager("nonexistent.json")
    assert sm.get_font("family") == "Segoe UI"
    assert sm.get_font("size") == 11


def test_get_color_fallback():
    sm = StyleManager("nonexistent.json")
    assert sm.get_color("definitely_not_a_color") == "#FFFFFF"


def test_get_size_and_spacing_fallback():
    sm = StyleManager("nonexistent.json")
    assert sm.get_size("nope") == 10
    assert sm.get_spacing("nope") == 10


def test_real_ui_styles_file_loads():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo_root, "ui_styles.json")
    if os.path.exists(path):
        sm = StyleManager(path)
        bg = sm.get_color("main_background")
        assert isinstance(bg, str) and bg.startswith("#")
