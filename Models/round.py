from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Round:
    page_id: str
    name: str
    play_date: Optional[datetime] = None
    course: Optional[List[str]] = None  # relation: コースのpage_id
    layout_out: Optional[List[str]] = None  # relation: OUTレイアウトのpage_id
    layout_in: Optional[List[str]] = None  # relation: INレイアウトのpage_id
    members: Optional[List[str]] = None  # relation: メンバーのpage_id（最大4名）
    
    @classmethod
    def from_notion(cls, data: dict):
        return cls(
            page_id=data.get("page_id"),
            name=data.get("name", ""),
            play_date=data.get("play_date"),
            course=data.get("course"),
            layout_out=data.get("layout_out"),
            layout_in=data.get("layout_in"),
            members=data.get("members")
        )
