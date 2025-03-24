from dataclasses import dataclass, field
from typing import List, Optional
from services.helpers import ExtractVersion, ExtractIPAddress
from models.peer import Peer
from models.user import User

@dataclass
class Jury:
    height: int
    juryid: str
    content_id: str
    content_type: int
    address: str
    reason: int
    verdict: int
    votes: int
    flag_count: int
    moders_count: int
    vote_count: int
    user: User

    def to_dict(self):
        return {
            "address": self.address,
            "height": self.height,
            "juryid": self.juryid,
            "content_id": self.content_id,
            "content_type": self.content_type,
            "reason": self.reason,
            "verdict": self.verdict,
            "votes": self.votes,
            "flag_count": self.flag_count,
            "moders_count": self.moders_count,
            "vote_count": self.vote_count,
            "user": self.user.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            address = data.get("address", ""),
            height = data.get("height", 0),
            juryid = data.get("juryid", ""),
            content_id = data.get("content_id", ""),
            content_type = data.get("content_type", 0),
            reason = data.get("reason", 0),
            verdict = data.get("verdict", 0),
            votes = data.get("votes", 0),
            flag_count = data.get("flag_count", 0),
            moders_count = data.get("moders_count", 0),
            vote_count = data.get("vote_count", 0),
            user = User.from_dict(data.get("user", {}))
        )
