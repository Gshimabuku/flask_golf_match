from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Layout:
    page_id: str
    name: str
    course: List[str]  # relation: コースのpage_id
    layout_name: Optional[str] = None
    par: Optional[int] = None
    
    @classmethod
    def from_notion(cls, data: dict):
        return cls(
            page_id=data.get("page_id"),
            name=data.get("name", ""),
            course=data.get("course", []),
            layout_name=data.get("layout_name"),
            par=data.get("par")
        )
