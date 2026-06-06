"""数据类 to_dict/from_dict 的混入基类。"""
from typing import Any, Dict


class SerializableMixin:
    """为 dataclass 提供默认 to_dict/from_dict。

    注意：默认实现对 tuple 字段可能返回 list。需要严格类型的子类请覆盖。
    """

    def to_dict(self) -> Dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)
