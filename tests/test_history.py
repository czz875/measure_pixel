"""History 撤销/恢复栈测试。"""
from src.core.history import History, HistoryState
from src.core.constants import MAX_HISTORY


def test_empty():
    h = History()
    assert len(h) == 0
    assert h.can_undo() is False
    assert h.can_redo() is False
    assert h.undo() is None
    assert h.redo() is None


def test_push_and_basic_undo_redo():
    h = History()
    h.push(HistoryState(segments=[{"a": 1}]))
    h.push(HistoryState(segments=[{"a": 2}]))
    assert len(h) == 2
    state = h.undo()
    assert state is not None and state.segments == [{"a": 1}]
    state = h.redo()
    assert state is not None and state.segments == [{"a": 2}]


def test_push_clears_redo_branch():
    h = History()
    h.push(HistoryState(segments=[{"a": 1}]))
    h.push(HistoryState(segments=[{"a": 2}]))
    h.undo()
    assert h.can_redo() is True
    h.push(HistoryState(segments=[{"a": 3}]))
    assert h.can_redo() is False


def test_max_size_enforced():
    h = History(max_size=3)
    for i in range(5):
        h.push(HistoryState(segments=[{"i": i}]))
    assert len(h) == 3
    assert h.current().segments == [{"i": 4}]


def test_undo_lower_bound():
    h = History()
    h.push(HistoryState(segments=[{"a": 1}]))
    assert h.can_undo() is False
    assert h.undo() is None


def test_polygon_field_preserved():
    h = History()
    h.push(HistoryState(polygons=[{"points": [(0, 0), (1, 0), (0, 1)], "image_index": 0}]))
    snap = h.current()
    assert snap is not None
    assert len(snap.polygons) == 1
    assert snap.polygons[0]["image_index"] == 0


def test_max_history_default_constant():
    assert MAX_HISTORY == 100
