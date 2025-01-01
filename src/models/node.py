from dataclasses import dataclass, field
from typing import List, Optional
from services.helpers import ExtractVersion, ExtractIPAddress
from models.peer import Peer

@dataclass
class Node:
    address: str
    version: Optional[str] = None
    time: Optional[int] = None
    height: Optional[int] = None
    public: Optional[bool] = None
    update: Optional[int] = None
    peers: Optional[List[Peer]] = None
    peer_count: Optional[int] = None

    def to_dict(self):
        r = {
            "address": self.address,
            "version": self.version,
            "time": self.time,
            "height": self.height,
            "public": self.public,
            "update": self.update,
        }
        if not self.peers is None:
            r['peers'] = [peer.to_dict() for peer in self.peers]
        if not self.peer_count is None:
            r['peer_count'] = self.peer_count
        return r
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            address = ExtractIPAddress(data.get("addr") if data.get("addr") else data.get("address")),
            version = ExtractVersion(data.get("version")),
            time = data.get("time"),
            height = data.get("height"),
            public = data.get("public"),
            update = data.get("update"),
            peer_count = data.get("peer_count")
        )
    

    
