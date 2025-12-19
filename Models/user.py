from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    page_id: str
    name: str
    display_name: Optional[str] = None
    
    @classmethod
    def from_notion(cls, data: dict):
        return cls(
            page_id=data.get("page_id"),
            name=data.get("name", ""),
            display_name=data.get("display_name")
        )
