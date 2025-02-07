from dataclasses import dataclass, field
from typing import List, Optional
from services.helpers import ExtractVersion, ExtractIPAddress
from models.peer import Peer

@dataclass
class Jury:
    height: int
    id: str
    content_id: str
    content_type: int
    address: str
    reason: int
    verdict: int
    checked: Optional[int] = 0

    def to_dict(self):
        return {
            "address": self.address,
            "height": self.height,
            "id": self.id,
            "content_id": self.content_id,
            "content_type": self.content_type,
            "reason": self.reason,
            "verdict": self.verdict,
            "checked": self.checked
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            address = data.get("address", ""),
            height = data.get("height", 0),
            id = data.get("id", ""),
            content_id = data.get("content_id", ""),
            content_type = data.get("content_type", 0),
            reason = data.get("reason", 0),
            verdict = data.get("verdict", 0),
            checked = data.get("checked", None)
        )
    

    
