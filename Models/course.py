from dataclasses import dataclass
from typing import Optional
from Const import course_type

@dataclass
class Course:
    page_id: str
    name: str
    course_type: str
    address: Optional[str] = None
    par: Optional[int] = None
    
    @property
    def type_display(self) -> str:
        """コースタイプの表示用名称を取得"""
        return course_type.get_display_name(self.course_type)

    @classmethod
    def from_notion(cls, data: dict):
        return cls(
            page_id=data.get("page_id"),
            name=data.get("name", ""),
            course_type=data.get("course_type", ""),
            address=data.get("address"),
            par=data.get("par")
        )
