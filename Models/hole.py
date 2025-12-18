from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Hole:
    page_id: str
    name: str
    layout: List[str]  # relation: レイアウトのpage_id
    hole_number: Optional[int] = None
    par: Optional[int] = None
    
    @classmethod
    def from_notion(cls, data: dict):
        return cls(
            page_id=data.get("page_id"),
            name=data.get("name", ""),
            layout=data.get("layout", []),
            hole_number=data.get("hole_number"),
            par=data.get("par")
        )
