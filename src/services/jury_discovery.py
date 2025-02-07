from typing import List, Optional
from models.node import Node
from models.peer import Peer
from aiohttp import ClientTimeout, ClientSession
import asyncio
import time
from datetime import datetime, UTC

import logging
log = logging.getLogger(__name__)

class JuryDiscovery:
    def __init__(self, mongodb_client):
        self.db = mongodb_client
        self.lock = asyncio.Lock()
        self.exit = False
        self.node = None

    """Запуск процесса обнаружения жюри"""
    async def discover(self):
        self.exit = False

        # Создаем и запускаем задачи для обнаружения пиров и узлов
        discover_new_juries_tasks = asyncio.create_task(self.discover_new_juries())
        discover_details_tasks = asyncio.create_task(self.discover_details_tasks())
        
        # Ожидаем завершения задач
        await asyncio.gather(discover_new_juries_tasks, discover_details_tasks)

    """Получение новых жюри"""
    async def discover_new_juries(self):
        while not self.exit:
            try:
                node = await self.get_active_node_instance()
                if node is None:
                    log.error("Активный узел не найден")
                    await asyncio.sleep(10)
                    continue

                # 1. Получаем максимальную высоту из базы данных
                max_height = await self.db.juries.find_one(
                    sort=[("height", -1)]
                )
                current_height = max_height["height"] if max_height else 0

                log.info(f"Текущая высота жюри: {current_height}")

                # 2. Запрашиваем жюри начиная с текущей высоты
                async with ClientSession() as session:
                    async with session.post(
                        f"http://{node.address}:38081/rpc/public",
                        json={
                            "method": "getalljury",
                            "params": [
                                current_height,  # topHeight 
                                0,  # pageStart
                                10,  # pageSize
                                "height",  # orderBy
                                False  # orderDesc
                            ]
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            juries = data.get("result", [])
                            
                            # 3. Добавляем новые жюри в базу данных
                            if juries:
                                for jury in juries:
                                    if 'height' not in jury or jury['height'] is None:
                                        continue
                                    
                                    log.info(f"Добавление нового жюри: {jury}")
                                    await self.db.juries.update_one(
                                        {"id": jury["id"]},
                                        {"$set": jury},
                                        upsert=True
                                    )
                                # 3.1 Ждем 0.1 секунду перед следующей итерацией
                                await asyncio.sleep(0.1)
                            else:
                                # 4. Если новых жюри нет, ждем 10 секунд
                                await asyncio.sleep(60)
                                
            except Exception as e:
                log.error(f"Ошибка при получении жюри: {e}")
                await asyncio.sleep(10)
    
    """Получение деталей жюри"""
    async def discover_details_tasks(self):
        while not self.exit:
            try:
                # Получаем жюри с вердиктом -1 и минимальным количеством проверок
                jury = await self.db.juries.find_one(
                    {"verdict": -1},
                    sort=[("checked", 1)]
                )

                if jury:
                    # Получаем активный узел
                    node = await self.get_active_node_instance()
                    if not node:
                        await asyncio.sleep(10)
                        continue

                    # Получаем актуальную информацию о жюри
                    async with ClientSession() as session:
                        async with session.post(
                            f"http://{node.address}:38081/rpc/public",
                            json={
                                "method": "getjury",
                                "params": [jury["id"]]
                            }
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                jury_details = data.get("result")

                                if jury_details and jury_details.get("verdict") not in [-1, None]:
                                    # Обновляем информацию в базе данных
                                    await self.db.juries.update_one(
                                        {"id": jury["id"]},
                                        {
                                            "$set": {
                                                "verdict": jury_details["verdict"],
                                                "checked": int(time.time())
                                            }
                                        }
                                    )

                await asyncio.sleep(10)

            except Exception as e:
                log.error(f"Ошибка при получении деталей жюри: {e}")
                await asyncio.sleep(10)

    """Получение адреса активного узла из базы данных"""
    async def get_active_node_instance(self) -> Optional[Node]:
        try:
            if not self.node is None:
                return self.node
            
            node = await self.db.nodes.find_one(
                {"public": True},
                sort=[("update", -1)]
            )

            return Node.from_dict(node)
        except Exception as e:
            log.error(f"Ошибка при получении активного узла: {e}")
            return None
