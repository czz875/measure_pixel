"""
数据持久化模块 - 文件处理器
"""
import json
import os
from typing import Optional, Dict, Any
from src.core.models import MeasurementData, LineSegment, AngleSegment, CircleSegment, RectangleSegment, PointToLineSegment, PolygonSegment


class FileHandler:
    """文件处理器"""
    
    @staticmethod
    def load_segments(file_path: str) -> Optional[MeasurementData]:
        """
        加载标注数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            测量数据对象
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return MeasurementData.from_dict(data)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def save_segments(file_path: str, measurement_data: MeasurementData) -> bool:
        """
        保存标注数据
        
        Args:
            file_path: 文件路径
            measurement_data: 测量数据对象
            
        Returns:
            是否保存成功
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(measurement_data.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False
    
    @staticmethod
    def get_segment_file_path(image_path: str) -> str:
        """
        获取标注文件路径
        
        Args:
            image_path: 图片路径
            
        Returns:
            标注文件路径
        """
        base, ext = os.path.splitext(image_path)
        return f"{base}_segments.json"
    
    @staticmethod
    def load_project(file_path: str) -> Optional[Dict[str, Any]]:
        """
        加载项目文件
        
        Args:
            file_path: 项目文件路径
            
        Returns:
            项目数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def save_project(file_path: str, project_data: Dict[str, Any]) -> bool:
        """
        保存项目文件
        
        Args:
            file_path: 项目文件路径
            project_data: 项目数据
            
        Returns:
            是否保存成功
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存项目失败: {e}")
            return False
    
    @staticmethod
    def export_to_csv(file_path: str, data: list, headers: list) -> bool:
        """
        导出数据到CSV
        
        Args:
            file_path: CSV文件路径
            data: 数据列表
            headers: 表头列表
            
        Returns:
            是否导出成功
        """
        try:
            import csv
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
