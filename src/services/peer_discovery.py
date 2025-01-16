from typing import List, Optional
from models.node import Node
from models.peer import Peer
from aiohttp import ClientTimeout, ClientSession
import asyncio
from datetime import datetime, UTC

import logging
log = logging.getLogger(__name__)

class PeerDiscovery:
    def __init__(self, mongodb_client, initial_peers: List[str]):
        self.db = mongodb_client
        self.initial_peers = initial_peers
        self.lock = asyncio.Lock()

    async def discover(self):
        """Начинает процесс обнаружения пиров и узлов"""

        # Создаем и запускаем задачи для обнаружения пиров и узлов
        # peer_discovery_task = asyncio.create_task(self.discover_peers())
        node_discovery_tasks = [asyncio.create_task(self.worker(i)) for i in range(1, 11)]
        
        # Ожидаем завершения задач
        await asyncio.gather(*node_discovery_tasks)

    async def worker(self, i: int):
        while True:
            node = await self.get_oldest_update_node(i)
            log.info(f"Worker: #{i} Update: {node.update if node else 'None'} Node: {node.address if node else 'None'}")
            try:
                if node:
                    await self.discover_info(node)
                    await self.discover_peers(node)
                await asyncio.sleep(5)
            except Exception as e:
                log.error(f"Ошибка при сканировании узла {node.address if node else 'None'}: {e}")

    async def discover_info(self, node: Node):
        try:
            node_info = await self.fetch_node_info(node)
            if node_info:
                await self.save_node_to_db(node_info)
            elif node.update and node.update < (int(datetime.now(UTC).timestamp()) - 60 * 30):
                await self.delete_node_from_db(node)
        except Exception as e:
            log.error(f"Ошибка при сканировании узла {node.address}: {e}")

    async def discover_peers(self, node: Node):
        try:
            peers = await self.fetch_peers_from_node(node)
            known_nodes = await self.load_known_nodes_from_db() or {}

            # Сохраняем пир как новый узел, если он не существует в базе данных
            for p in peers:
                # Вставка нового узла в базу данных
                if p.address in known_nodes:
                    # Обновляем информацию узла, если высота пира больше высоты узла
                    exist_node = known_nodes[p.address]
                    if (p.synced_blocks or 0) > (exist_node.height or 0):
                        exist_node.height = p.synced_blocks
                    exist_node.version = p.version
                    exist_node.update = int(datetime.now(UTC).timestamp())
                    await self.save_node_to_db(exist_node)
                else:
                    new_node = Node(address=p.address, height=p.synced_blocks, version=p.version, update=int(datetime.now(UTC).timestamp()))
                    await self.save_node_to_db(new_node)
        except Exception as e:
            log.error(f"Ошибка при сканировании пиров узла {node.address}: {e}")

    async def load_known_nodes_from_db(self) -> dict[str, Node]:
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
        return known_nodes

    async def get_oldest_update_node(self, i) -> Optional[Node]:
        """Получение самой старой ноды по полю update из базы данных"""
        try:
            async with self.lock:
                async for doc in self.db.nodes.find({}).sort("fetch", 1).limit(1):
                    node = Node.from_dict(doc)
                    if not node:
                        nodes = await self.load_known_nodes_from_db()
                        node = nodes[list(nodes.keys())[0]]

                    node.fetch = int(datetime.now(UTC).timestamp())
                    await self.db.nodes.update_one(
                        {"address": node.address},
                        {"$set": node.to_dict()},
                        upsert=True
                    )
                    return node
        except Exception as e:
            log.error(f"Ошибка при получении самой старой ноды из базы данных: {e}")
            return None

    async def save_node_to_db(self, node: Node):
        """Сохранение известного пира в базу данных"""
        address = node.address
        try:
            async with self.lock:
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
            async with self.lock:
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
                    
                    # Удаляем всех пиров для текущего узла перед сохранением новых
                    try:
                        async with self.lock:
                            await self.db.peers.delete_many({"address_node": node.address})
                            log.info(f"Удалены старые записи пиров для узла {node.address}")
                    except Exception as e:
                        log.error(f"Ошибка при удалении старых записей пиров для узла {node.address}: {e}")
                    
                    # Сохраняем новые пиры
                    for peer_data in data['result']:
                        peer = Peer.from_dict(peer_data)
                        peer.address_node = node.address
                        await self.save_peer_to_db(node, peer)
                        peers.append(peer)
        except Exception as e:
            log.warning(f"Ошибка при получении пиров от {node.address}: {e}")
            return []

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
                    result['update'] = int(datetime.now(UTC).timestamp())
                    result['fetch'] = int(datetime.now(UTC).timestamp())
                    node_info = Node.from_dict(result)

                    log.info(f"Информация об узле {node.address} получена успешно")
                    return node_info
        except Exception as e:
            log.warning(f"Ошибка при получении информации об узле {node.address}: {e}")
            return None

    async def delete_node_from_db(self, node: Node):
        """Удаление узла из базы данных"""
        try:
            async with self.lock:
                # Удаляем связанные записи пиров
                peers_result = await self.db.peers.delete_many({"address_node": node.address})
                if peers_result.deleted_count > 0:
                    log.info(f"Удалено {peers_result.deleted_count} записей пиров для узла {node.address}")

                # Удаляем узел
                result = await self.db.nodes.delete_one({"address": node.address})
                if result.deleted_count > 0:
                    log.info(f"Узел {node.address} удален из базы данных")
        except Exception as e:
            log.error(f"Ошибка при удалении узла {node.address} из базы данных: {e}")
  