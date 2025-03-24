from dataclasses import dataclass, field
from typing import List, Optional
from services.helpers import ExtractVersion, ExtractIPAddress
from models.peer import Peer

@dataclass
class User:
    name: str
    reputation: int
    likers_count: int

    def to_dict(self):
        return {
            "name": self.name,
            "reputation": self.reputation,
            "likers_count": self.likers_count
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name = data.get("name", ""),
            reputation = data.get("reputation", 0),
            likers_count = data.get("likers_count", 0)
        )
