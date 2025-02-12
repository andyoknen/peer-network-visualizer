from dataclasses import dataclass
from typing import Optional
from services.helpers import ExtractVersion, ExtractIPAddress

@dataclass
class Peer:
    address: str
    address_node: str
    relaytxes: Optional[bool] = None
    lastsend: Optional[int] = None
    lastrecv: Optional[int] = None
    conntime: Optional[int] = None
    timeoffset: Optional[int] = None
    pingtime: Optional[int] = None
    version: Optional[str] = None
    inbound: Optional[bool] = None
    startingheight: Optional[int] = None
    synced_headers: Optional[int] = None
    synced_blocks: Optional[int] = None
        
    def to_dict(self):
        return {
            "address": self.address,
            "address_node": self.address_node,
            "relaytxes": self.relaytxes,
            "lastsend": self.lastsend,
            "lastrecv": self.lastrecv,
            "conntime": self.conntime,
            "timeoffset": self.timeoffset,
            "pingtime": self.pingtime,
            "version": self.version,
            "inbound": self.inbound,
            "startingheight": self.startingheight,
            "synced_headers": self.synced_headers,
            "synced_blocks": self.synced_blocks,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            address = ExtractIPAddress(data.get("addr") if data.get("addr") else data.get("address") ),
            address_node = str(data.get('address_node')),
            relaytxes = data.get("relaytxes"),
            lastsend = data.get("lastsend"),
            lastrecv = data.get("lastrecv"),
            conntime = data.get("conntime"),
            timeoffset = data.get("timeoffset"),
            pingtime = data.get("pingtime"),
            version = ExtractVersion(data.get("version")),
            inbound = data.get("inbound"),
            startingheight = data.get("startingheight"),
            synced_headers = data.get("synced_headers"),
            synced_blocks = data.get("synced_blocks"),
        )
