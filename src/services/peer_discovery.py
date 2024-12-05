from typing import List, Optional
from models.node import Node
from models.peer import Peer
from aiohttp import ClientTimeout, ClientSession
import asyncio
import time

import logging
log = logging.getLogger(__name__)

class PeerDiscovery:
    def __init__(self, mongodb_client, initial_peers: List[str]):
        self.db = mongodb_client
        self.initial_peers = initial_peers
        self.lock = asyncio.Lock()

    async def discover_peers(self):
        while True:
            try:
                known_nodes = await self.load_known_nodes_from_db() or {}
                for address, node in known_nodes.items():
                    peers = await self.fetch_peers_from_node(node)
                    # Сохраняем пир как новый узел, если он не существует в базе данных
                    for p in peers:
                        # Вставка нового узла в базу данных
                        if p.address in known_nodes:
                            # Обновляем информацию узла, если высота пира больше высоты узла
                            exist_node = known_nodes[p.address]
                            if (p.synced_blocks or 0) > (exist_node.height or 0):
                                exist_node.height = p.synced_blocks
                                async with self.lock:
                                    exist_node.update = int(time.time())
                                    await self.save_node_to_db(exist_node)
                        else:
                            new_node = Node(address=p.address, height=p.synced_blocks, version=p.version, update=int(time.time()))
                            async with self.lock:
                                await self.save_node_to_db(new_node)
                await asyncio.sleep(1)
            except Exception as e:
                log.error(f"Ошибка при сканировании пиров: {e}")

    async def discover_nodes(self, i: int):
        while True:
            try:
                node = await self.get_oldest_update_node()
                if node:
                    node_info = await self.fetch_node_info(node)
                    if node_info:
                        await self.save_node_to_db(node_info)
                await asyncio.sleep(1)
            except Exception as e:
                log.error(f"Ошибка при сканировании узлов: {e}")

    async def load_known_nodes_from_db(self) -> Optional[dict[str, Node]]:
        """Загрузка известных пиров из базы данных"""
        known_nodes = { peer: Node(peer) for peer in self.initial_peers }
        try:
            async with self.lock:
                async for doc in self.db.nodes.find({}):
                    node = Node.from_dict(doc)
                    known_nodes[node.address] = node
                return known_nodes
        except Exception as e:
            log.error(f"Ошибка при загрузке известных пиров из базы данных: {e}")
        return None

    async def get_oldest_update_node(self) -> Optional[Node]:
        """Получение самой старой ноды по полю update из базы данных"""
        try:
            async with self.lock:
                async for doc in self.db.nodes.find({}).sort("update", 1).limit(1):
                    node = Node.from_dict(doc)
                    node.update = int(time.time())
                    await self.save_node_to_db(node)
                    return node
        except Exception as e:
            log.error(f"Ошибка при получении самой старой ноды из базы данных: {e}")
            return None

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

    async def fetch_peers_from_node(self, node: Node) -> List[Peer]:
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
                        peer = Peer.from_dict(peer_data)
                        peer.address_node = node.address
                        await self.save_peer_to_db(node, peer)
                        peers.append(peer)
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
                    timeout = ClientTimeout(total=5)
                ) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    if not data.get('result'):
                        return None
                    
                    result = data['result']
                    result['public'] = True
                    result['address'] = node.address
                    result['height'] = result['lastblock']['height']
                    node_info = Node.from_dict(result)

                    log.info(f"Информация об узле {node.address} получена успешно")
                    return node_info
        except Exception as e:
            log.warning(f"Ошибка при получении информации об узле {node.address}: {e}")
            return None
  