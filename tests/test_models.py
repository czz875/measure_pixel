"""
测试数据模型
"""
import pytest
from src.core.models import LineSegment, AngleSegment, PolygonSegment, MeasurementData


def test_line_segment_to_dict():
    """测试线段转换为字典"""
    segment = LineSegment(points=[(0, 0), (100, 100)], image_index=0)
    data = segment.to_dict()
    
    assert data['points'] == [[0, 0], [100, 100]]
    assert data['image_index'] == 0


def test_line_segment_from_dict():
    """测试从字典创建线段"""
    data = {
        'points': [[0, 0], [100, 100]],
        'image_index': 0
    }
    segment = LineSegment.from_dict(data)
    
    assert segment.points == [(0, 0), (100, 100)]
    assert segment.image_index == 0


def test_angle_segment_to_dict():
    """测试角度转换为字典"""
    angle = AngleSegment(
        vertex_point=(50, 50),
        point1=(0, 50),
        point2=(100, 50),
        image_index=0
    )
    data = angle.to_dict()
    
    assert data['vertex_point'] == [50, 50]
    assert data['point1'] == [0, 50]
    assert data['point2'] == [100, 50]
    assert data['image_index'] == 0


def test_angle_segment_from_dict():
    """测试从字典创建角度"""
    data = {
        'vertex_point': [50, 50],
        'point1': [0, 50],
        'point2': [100, 50],
        'image_index': 0
    }
    angle = AngleSegment.from_dict(data)
    
    assert angle.vertex_point == (50, 50)
    assert angle.point1 == (0, 50)
    assert angle.point2 == (100, 50)
    assert angle.image_index == 0


def test_measurement_data_to_dict():
    """测试测量数据转换为字典"""
    segment = LineSegment(points=[(0, 0), (100, 100)], image_index=0)
    angle = AngleSegment(
        vertex_point=(50, 50),
        point1=(0, 50),
        point2=(100, 50),
        image_index=0
    )
    measurement_data = MeasurementData(
        segments=[segment], 
        angles=[angle],
        circles=[],
        rectangles=[],
        point_to_lines=[],
        polygons=[]
    )
    
    data = measurement_data.to_dict()
    
    assert len(data['segments']) == 1
    assert len(data['angles']) == 1


def test_measurement_data_from_dict():
    """测试从字典创建测量数据"""
    data = {
        'segments': [
            {
                'points': [[0, 0], [100, 100]],
                'image_index': 0
            }
        ],
        'angles': [
            {
                'vertex_point': [50, 50],
                'point1': [0, 50],
                'point2': [100, 50],
                'image_index': 0
            }
        ]
    }
    measurement_data = MeasurementData.from_dict(data)
    
    assert len(measurement_data.segments) == 1
    assert len(measurement_data.angles) == 1


def test_polygon_segment_to_dict():
    """测试多边形转换为字典"""
    polygon = PolygonSegment(points=[(0, 0), (100, 0), (100, 100), (0, 100)], image_index=0)
    data = polygon.to_dict()
    
    assert data['points'] == [[0, 0], [100, 0], [100, 100], [0, 100]]
    assert data['image_index'] == 0


def test_polygon_segment_from_dict():
    """测试从字典创建多边形"""
    data = {
        'points': [[0, 0], [100, 0], [100, 100], [0, 100]],
        'image_index': 0
    }
    polygon = PolygonSegment.from_dict(data)
    
    assert polygon.points == [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert polygon.image_index == 0


def test_polygon_area_calculation():
    """测试多边形面积计算"""
    square = PolygonSegment(points=[(0, 0), (100, 0), (100, 100), (0, 100)], image_index=0)
    assert square.area == 10000
    
    triangle = PolygonSegment(points=[(0, 0), (100, 0), (50, 100)], image_index=0)
    assert abs(triangle.area - 5000) < 1


def test_polygon_perimeter_calculation():
    """测试多边形周长计算"""
    square = PolygonSegment(points=[(0, 0), (100, 0), (100, 100), (0, 100)], image_index=0)
    assert abs(square.perimeter - 400) < 1
    
    triangle = PolygonSegment(points=[(0, 0), (100, 0), (50, 100)], image_index=0)
    assert abs(triangle.perimeter - 323.6) < 1


def test_measurement_data_with_polygons():
    """测试包含多边形的测量数据"""
    polygon = PolygonSegment(points=[(0, 0), (100, 0), (100, 100), (0, 100)], image_index=0)
    measurement_data = MeasurementData(
        segments=[],
        angles=[],
        circles=[],
        rectangles=[],
        point_to_lines=[],
        polygons=[polygon]
    )
    
    data = measurement_data.to_dict()
    assert len(data['polygons']) == 1
    
    loaded_data = MeasurementData.from_dict(data)
    assert len(loaded_data.polygons) == 1
    assert loaded_data.polygons[0].area == 10000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
