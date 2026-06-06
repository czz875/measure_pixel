"""
数据模型定义
"""
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class LineSegment:
    """线段数据模型"""
    points: List[Tuple[float, float]]
    image_index: int
    
    def to_dict(self):
        """转换为字典"""
        return {
            'points': [[float(x), float(y)] for x, y in self.points],
            'image_index': self.image_index
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(
            points=[tuple(p) for p in data['points']],
            image_index=data['image_index']
        )


@dataclass
class AngleSegment:
    """角度数据模型"""
    vertex_point: Tuple[float, float]
    point1: Tuple[float, float]
    point2: Tuple[float, float]
    image_index: int
    
    def to_dict(self):
        """转换为字典"""
        return {
            'vertex_point': [float(self.vertex_point[0]), float(self.vertex_point[1])],
            'point1': [float(self.point1[0]), float(self.point1[1])],
            'point2': [float(self.point2[0]), float(self.point2[1])],
            'image_index': self.image_index
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(
            vertex_point=tuple(data['vertex_point']),
            point1=tuple(data['point1']),
            point2=tuple(data['point2']),
            image_index=data['image_index']
        )


@dataclass
class CircleSegment:
    """圆形数据模型"""
    center: Tuple[float, float]
    radius_point: Tuple[float, float]
    image_index: int
    
    @property
    def radius(self):
        """计算半径"""
        return math.sqrt((self.radius_point[0] - self.center[0])**2 + 
                        (self.radius_point[1] - self.center[1])**2)
    
    @property
    def diameter(self):
        """计算直径"""
        return self.radius * 2
    
    @property
    def circumference(self):
        """计算周长"""
        return 2 * math.pi * self.radius
    
    @property
    def area(self):
        """计算面积"""
        return math.pi * self.radius ** 2
    
    def to_dict(self):
        """转换为字典"""
        return {
            'center': [float(self.center[0]), float(self.center[1])],
            'radius_point': [float(self.radius_point[0]), float(self.radius_point[1])],
            'image_index': self.image_index
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建，兼容旧字段 point_on_circle。"""
        center = tuple(data['center'])
        radius_point = tuple(
            data.get('radius_point') or data.get('point_on_circle') or (0.0, 0.0)
        )
        return cls(center=center, radius_point=radius_point, image_index=data['image_index'])


@dataclass
class RectangleSegment:
    """矩形数据模型"""
    points: List[Tuple[float, float]]
    image_index: int
    
    @property
    def width(self):
        """计算宽度"""
        if len(self.points) >= 2:
            return abs(self.points[1][0] - self.points[0][0])
        return 0
    
    @property
    def height(self):
        """计算高度"""
        if len(self.points) >= 2:
            return abs(self.points[1][1] - self.points[0][1])
        return 0
    
    @property
    def perimeter(self):
        """计算周长"""
        return 2 * (self.width + self.height)
    
    @property
    def area(self):
        """计算面积"""
        return self.width * self.height
    
    def to_dict(self):
        """转换为字典"""
        return {
            'points': [[float(x), float(y)] for x, y in self.points],
            'image_index': self.image_index
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(
            points=[tuple(p) for p in data['points']],
            image_index=data['image_index']
        )


@dataclass
class PointToLineSegment:
    """点到线距离数据模型"""
    point: Tuple[float, float]
    line_start: Tuple[float, float]
    line_end: Tuple[float, float]
    image_index: int
    
    @property
    def distance(self):
        """计算点到线的距离"""
        x0, y0 = self.point
        x1, y1 = self.line_start
        x2, y2 = self.line_end
        
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def to_dict(self):
        """转换为字典"""
        return {
            'point': [float(self.point[0]), float(self.point[1])],
            'line_start': [float(self.line_start[0]), float(self.line_start[1])],
            'line_end': [float(self.line_end[0]), float(self.line_end[1])],
            'image_index': self.image_index
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(
            point=tuple(data['point']),
            line_start=tuple(data['line_start']),
            line_end=tuple(data['line_end']),
            image_index=data['image_index']
        )


@dataclass
class PolygonSegment:
    """多边形数据模型"""
    points: List[Tuple[float, float]]
    image_index: int
    
    @property
    def area(self):
        """计算多边形面积（使用鞋带公式）"""
        if len(self.points) < 3:
            return 0
        
        n = len(self.points)
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += self.points[i][0] * self.points[j][1]
            area -= self.points[j][0] * self.points[i][1]
        
        return abs(area) / 2
    
    @property
    def perimeter(self):
        """计算多边形周长"""
        if len(self.points) < 2:
            return 0
        
        perimeter = 0
        n = len(self.points)
        for i in range(n):
            j = (i + 1) % n
            dx = self.points[j][0] - self.points[i][0]
            dy = self.points[j][1] - self.points[i][1]
            perimeter += math.sqrt(dx**2 + dy**2)
        
        return perimeter
    
    def to_dict(self):
        """转换为字典"""
        return {
            'points': [[float(p[0]), float(p[1])] for p in self.points],
            'image_index': self.image_index
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(
            points=[tuple(p) for p in data['points']],
            image_index=data['image_index']
        )


@dataclass
class MeasurementData:
    """测量数据集合"""
    segments: List[LineSegment]
    angles: List[AngleSegment]
    circles: List[CircleSegment]
    rectangles: List[RectangleSegment]
    point_to_lines: List[PointToLineSegment]
    polygons: List[PolygonSegment]
    
    def to_dict(self):
        """转换为字典"""
        return {
            'segments': [seg.to_dict() for seg in self.segments],
            'angles': [angle.to_dict() for angle in self.angles],
            'circles': [circle.to_dict() for circle in self.circles],
            'rectangles': [rect.to_dict() for rect in self.rectangles],
            'point_to_lines': [ptl.to_dict() for ptl in self.point_to_lines],
            'polygons': [poly.to_dict() for poly in self.polygons]
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(
            segments=[LineSegment.from_dict(seg) for seg in data.get('segments', [])],
            angles=[AngleSegment.from_dict(angle) for angle in data.get('angles', [])],
            circles=[CircleSegment.from_dict(circle) for circle in data.get('circles', [])],
            rectangles=[RectangleSegment.from_dict(rect) for rect in data.get('rectangles', [])],
            point_to_lines=[PointToLineSegment.from_dict(ptl) for ptl in data.get('point_to_lines', [])],
            polygons=[PolygonSegment.from_dict(poly) for poly in data.get('polygons', [])]
        )
