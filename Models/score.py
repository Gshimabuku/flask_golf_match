from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Score:
    page_id: str
    name: str
    round: Optional[List[str]] = None  # relation: ラウンドのpage_id
    user: Optional[List[str]] = None  # relation: ユーザーのpage_id
    hole: Optional[List[str]] = None  # relation: ホールのpage_id
    hole_number: Optional[int] = None
    stroke: Optional[int] = None
    putt: Optional[int] = None
    olympic: Optional[str] = None  # select: gold, silver, bronze, iron, diamond
    snake: Optional[int] = None
    snake_out: Optional[bool] = None
    nearpin: Optional[bool] = None
    
    @classmethod
    def from_notion(cls, data: dict):
        return cls(
            page_id=data.get("page_id"),
            name=data.get("name", ""),
            round=data.get("round"),
            user=data.get("user"),
            hole=data.get("hole"),
            hole_number=data.get("hole_number"),
            stroke=data.get("stroke"),
            putt=data.get("putt"),
            olympic=data.get("olympic"),
            snake=data.get("snake"),
            snake_out=data.get("snake_out"),
            nearpin=data.get("nearpin")
        )
