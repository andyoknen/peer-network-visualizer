from typing import List, Set, Optional
import aiohttp
from models.node import Node, Peer, LastBlock, Ports
import re

import logging
log = logging.getLogger(__name__)

class PeerDiscovery:
    def __init__(self, initial_peers: List[str]):
        self.known_peers = {peer: Node(peer) for peer in initial_peers}

    async def discover_peers(self):
        new_peers = []

        for address, peer in self.known_peers.items():
            # Получаем информацию об узле перед поиском новых пиров
            node_info = await self.get_node_info(peer)
            if node_info:
                self.known_peers[address] = node_info

            # Получаем список пиров от текущего узла
            new_peers.extend(await self.fetch_peers_from_node(peer))

        for p in new_peers:
            if p.address not in self.known_peers or not self.known_peers[p.address].chain:
                self.known_peers[p.address] = p

    async def fetch_peers_from_node(self, peer: Node) -> Optional[Node]:
        """Получение списка пиров от текущего узла"""
        peers = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'http://{peer.address}:38081/rpc/public/',
                    json={
                        "method": "getpeerinfo",
                        "params": []
                    },
                    timeout=5
                ) as response:
                    
                    if response.status != 200:
                        return
                    
                    data = await response.json()
                    if not data.get('result'):
                        return
                    
                    for peer_data in data['result']:
                        peer_new = Peer(**peer_data)
                        peer_new.addr = self.extract_ip_address(peer_new.addr)
                        peers.append(Node(peer_new))

        except Exception as e:
            log.warning(f"Ошибка при получении пиров от {peer.address}: {e}")

        log.info(f"Пиров от {peer.address} получено: {len(peers)}")
        return peers
            
    async def get_node_info(self, node: Node) -> Optional[Node]:
        """Получение информации об узле"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'http://{node.address}:38081/rpc/public/',
                    json={
                        "method": "getnodeinfo",
                        "params": []
                    },
                    timeout=5
                ) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    if not data.get('result'):
                        return None
                    
                    result = data['result']
                    node_info = Node(node.address)

                    node_info.version = result['version']
                    node_info.time = result['time']
                    node_info.chain = result['chain']
                    node_info.proxy = result['proxy']
                    node_info.netstakeweight = result['netstakeweight']
                    node_info.proxies = result['proxies']
                    node_info.last_block = LastBlock(**data['result']['lastblock'])
                    node_info.ports = Ports(**data['result']['ports'])

                    log.info(f"Информация об узле {node.address} получена успешно")
                    return node_info
        except Exception as e:
            log.warning(f"Ошибка при получении информации об узле {node.address}: {e}")
            return None
    
    def extract_ip_address(self, input_string: str):
        # Регулярное выражение для поиска IPv4 и IPv6 адресов
        ip_pattern = r'(?:(?:\d{1,3}\.){3}\d{1,3}|[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4}){7})'
        
        # Поиск первого совпадения
        match = re.search(ip_pattern, input_string)
        
        if match:
            return match.group(0)
        
        return None
    