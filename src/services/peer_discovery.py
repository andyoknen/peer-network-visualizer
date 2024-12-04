from typing import List, Optional
from models.node import Node, LastBlock, Ports
from models.peer import Peer
from aiohttp import ClientTimeout, ClientSession
import asyncio

import logging
log = logging.getLogger(__name__)

class PeerDiscovery:
    def __init__(self, mongodb_client, initial_peers: List[str]):
        self.db = mongodb_client
        self.known_peers = {peer: Node(peer) for peer in initial_peers}

    async def discover_peers(self):
        await self.load_known_peers_from_db()

        while True:
            try:
                new_peers = []

                for address, peer in self.known_peers.items():
                    # Получаем информацию об узле перед поиском новых пиров
                    node_info = await self.fetch_node_info(peer)
                    if node_info:
                        self.known_peers[address] = node_info
                        await self.save_node_to_db(node_info)

                    # Получаем список пиров от текущего узла
                    new_peers.extend(await self.fetch_peers_from_node(peer))

                for p in new_peers:
                    if p.address not in self.known_peers or not self.known_peers[p.address].chain:
                        self.known_peers[p.address] = p
                        await self.save_node_to_db(p)

                await asyncio.sleep(300)  # 5 минут
            except Exception as e:
                log.error(f"Ошибка при сканировании узлов: {e}")
                await asyncio.sleep(60)  # Ожидание 1 минута при ошибке

    async def load_known_peers_from_db(self):
        """Загрузка известных пиров из базы данных"""
        try:
            async for doc in self.db.nodes.find({}):
                node = Node.from_dict(doc)
                self.known_peers[node.address] = node
            log.info("Известные пиры успешно загружены из базы данных")
        except Exception as e:
            log.error(f"Ошибка при загрузке известных пиров из базы данных: {e}")

    async def save_node_to_db(self, node: Node):
        """Сохранение известного пира в базу данных"""
        address = node.address
        try:
            await self.db.nodes.update_one(
                {"address": address},
                {"$set": node.to_dict()},
                upsert=True
            )
            log.info(f"Узел {address} сохранен в базе данных")
        except Exception as e:
            log.error(f"Ошибка при сохранении узла {address} в базе данных: {e}")

    async def save_peer_to_db(self, node: Node, peer: Peer):
        """Сохранение информации о пирах в базу данных"""
        try:
            await self.db.peers.update_one(
                {"address_node": node.address, "address": peer.address},
                {"$set": peer.to_dict()},
                upsert=True
            )
            log.info(f"Информация о пире {peer.address} сохранена в базе данных")
        except Exception as e:
            log.error(f"Ошибка при сохранении информации о пире {peer.address}: {e}")

    async def fetch_peers_from_node(self, node: Node) -> List[Node]:
        """Получение списка пиров от текущего узла"""
        peers = []

        try:
            async with ClientSession() as session:
                async with session.post(
                    f'http://{node.address}:38081/rpc/public/',
                    json = {
                        "method": "getpeerinfo",
                        "params": []
                    },
                    timeout = ClientTimeout(total=5)
                ) as response:
                    
                    if response.status != 200:
                        return []
                    
                    data = await response.json()
                    if not data.get('result'):
                        return []
                    
                    for peer_data in data['result']:
                        peer_new = Peer.from_dict(peer_data)
                        peer_new.address_node = node.address
                        await self.save_peer_to_db(node, peer_new)

                        node_new = Node.from_dict(peer_data)
                        node_new.lastblock = LastBlock()
                        node_new.lastblock.height = peer_new.synced_blocks
                        peers.append(node_new)


        except Exception as e:
            log.warning(f"Ошибка при получении пиров от {node.address}: {e}")

        log.info(f"Пиров от {node.address} получено: {len(peers)}")
        return peers

    async def fetch_node_info(self, node: Node) -> Optional[Node]:
        """Получение информации об узле"""
        try:
            async with ClientSession() as session:
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
                    result['address'] = node.address
                    node_info = Node.from_dict(result)

                    log.info(f"Информация об узле {node.address} получена успешно")
                    return node_info
        except Exception as e:
            log.warning(f"Ошибка при получении информации об узле {node.address}: {e}")
            return None
  