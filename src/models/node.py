from dataclasses import dataclass
from typing import List, Optional
from models.helpers import ExtractVersion, ExtractIPAddress

@dataclass
class LastBlock:
    height: Optional[int] = None
    hash: Optional[str] = None
    time: Optional[int] = None
    ntx: Optional[int] = None

    def to_dict(self):
        return {
            "height": self.height,
            "hash": self.hash,
            "time": self.time,
            "ntx": self.ntx,
        }
    
    @classmethod
    def from_dict(cls, data: Optional[dict] = None):
        return cls(
            height=data.get("height"),
            hash=data.get("hash"),
            time=data.get("time"),
            ntx=data.get("ntx"),
        ) if data is not None else None

@dataclass
class Ports:
    node: Optional[int] = None
    api: Optional[int] = None
    rest: Optional[int] = None
    wss: Optional[int] = None
    http: Optional[int] = None
    https: Optional[int] = None

    def to_dict(self):
        return {
            "node": self.node,
            "api": self.api,
            "rest": self.rest,
            "wss": self.wss,
            "http": self.http,
            "https": self.https,
        }
    
    @classmethod
    def from_dict(cls, data: Optional[dict] = None):
        return cls(
            node=data.get("node"),
            api=data.get("api"),
            rest=data.get("rest"),
            wss=data.get("wss"),
            http=data.get("http"),
            https=data.get("https"),
        ) if data is not None else None

@dataclass
class Node:
    address: str
    version: Optional[str] = None
    time: Optional[int] = None
    chain: Optional[str] = None
    proxy: Optional[bool] = None
    netstakeweight: Optional[int] = None
    proxies: Optional[List[str]] = None
    lastblock: Optional[LastBlock] = None
    ports: Optional[Ports] = None

    def to_dict(self):
        return {
            "address": self.address,
            "version": self.version,
            "time": self.time,
            "chain": self.chain,
            "proxy": self.proxy,
            "netstakeweight": self.netstakeweight,
            "proxies": self.proxies,
            "lastblock": self.lastblock.to_dict() if self.lastblock else None,
            "ports": self.ports.to_dict() if self.ports else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            address = ExtractIPAddress(data.get("addr") if data.get("addr") else data.get("address")),
            version = data.get("version"),
            time = data.get("time"),
            chain = data.get("chain"),
            proxy = data.get("proxy"),
            netstakeweight = data.get("netstakeweight"),
            proxies = data.get("proxies"),
            lastblock = LastBlock.from_dict(data.get("lastblock")) if data.get("lastblock") else None,
            ports = Ports.from_dict(data.get("ports")) if data.get("ports") else None,
        )
    

    
