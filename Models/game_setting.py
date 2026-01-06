from dataclasses import dataclass
from typing import Optional, List

@dataclass
class GameSetting:
    page_id: str
    name: str
    round: Optional[List[str]] = None  # relation: ラウンドのpage_id
    gold: Optional[int] = None
    silver: Optional[int] = None
    bronze: Optional[int] = None
    iron: Optional[int] = None
    diamond: Optional[int] = None
    snake: Optional[str] = None  # select: All or Separate
    snake_rate: Optional[int] = None  # ヘビのレート
    nearpin: Optional[bool] = None
    nearpin_rate: Optional[int] = None  # ニアピンのレート
    olympic_member: Optional[List[str]] = None  # relation: オリンピック参加メンバーのpage_id
    snake_member: Optional[List[str]] = None  # relation: ヘビ参加メンバーのpage_id
    nearpin_member: Optional[List[str]] = None  # relation: ニアピン参加メンバーのpage_id
    
    @classmethod
    def from_notion(cls, data: dict):
        return cls(
            page_id=data.get("page_id"),
            name=data.get("name", ""),
            round=data.get("round"),
            gold=data.get("gold"),
            silver=data.get("silver"),
            bronze=data.get("bronze"),
            iron=data.get("iron"),
            diamond=data.get("diamond"),
            snake=data.get("snake"),
            snake_rate=data.get("snake_rate"),
            nearpin=data.get("nearpin"),
            nearpin_rate=data.get("nearpin_rate"),
            olympic_member=data.get("olympic_member"),
            snake_member=data.get("snake_member"),
            nearpin_member=data.get("nearpin_member")
        )
