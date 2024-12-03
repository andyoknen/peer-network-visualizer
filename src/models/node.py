import re
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Peer:
    addr: Optional[str] = None
    services: Optional[str] = None
    relaytxes: Optional[bool] = None
    lastsend: Optional[int] = None
    lastrecv: Optional[int] = None
    conntime: Optional[int] = None
    timeoffset: Optional[int] = None
    pingtime: Optional[int] = None
    protocol: Optional[int] = None
    version: Optional[str] = None
    inbound: Optional[bool] = None
    startingheight: Optional[int] = None
    whitelisted: Optional[bool] = None
    banscore: Optional[int] = None
    synced_headers: Optional[int] = None
    synced_blocks: Optional[int] = None

    def Version(self) -> str:
        match = re.search(r'/Satoshi:([^/]+)/', self.version)
        if match:
            return match.group(1)
        return None

@dataclass
class LastBlock:
    height: Optional[int] = None
    hash: Optional[str] = None
    time: Optional[int] = None
    ntx: Optional[int] = None

@dataclass
class Ports:
    node: Optional[int] = None
    api: Optional[int] = None
    rest: Optional[int] = None
    wss: Optional[int] = None
    http: Optional[int] = None
    https: Optional[int] = None

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

    def __init__(self, data: any):
        if type(data) is str:
            self.address = data

        if type(data) is Peer:
            self.address = data.addr
            self.version = data.Version()
            self.lastblock = LastBlock()
            self.lastblock.height = data.synced_blocks

    
