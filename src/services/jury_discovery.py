from typing import Optional
from models.node import Node
from models.jury import Jury
from models.user import User
from aiohttp import ClientSession
import asyncio

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
        discover_verdict_tasks = asyncio.create_task(self.discover_verdict_tasks())
        
        # Ожидаем завершения задач
        await asyncio.gather(discover_new_juries_tasks, discover_verdict_tasks)

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
                                for item in juries:
                                    jury = item["jury"]

                                    if 'height' not in jury or jury['height'] is None:
                                        continue
                                    
                                    j = Jury.from_dict(jury)
                                    if 'userprofile' in item:
                                        j.user = User.from_dict(item['userprofile'])
                                    else:
                                        j.user = User.from_dict(item)
                                    
                                    log.info(f"Добавление нового жюри: {jury}")
                                    await self.db.juries.update_one(
                                        {"juryid": jury["juryid"]},
                                        {"$set": j.to_dict()},
                                        upsert=True
                                    )

                                    # Get details
                                    await self.discover_details(j)

                                # 3.1 Ждем 0.1 секунду перед следующей итерацией
                                await asyncio.sleep(0.1)
                            else:
                                # 4. Если новых жюри нет, ждем 10 секунд
                                await asyncio.sleep(60)
                                
            except Exception as e:
                log.error(f"Ошибка при получении жюри: {e}")
                await asyncio.sleep(10)
    
    """Получение деталей жюри"""
    async def discover_verdict_tasks(self):
        while not self.exit:
            try:
                # Получаем активный узел
                node = await self.get_active_node_instance()
                if not node:
                    await asyncio.sleep(10)
                    continue

                async for jury in self.db.juries.find({"verdict": -1}):
                    # Получаем актуальную информацию о жюри
                    async with ClientSession() as session:
                        async with session.post(
                            f"http://{node.address}:38081/rpc/public",
                            json={
                                "method": "getjury",
                                "params": [jury["juryid"]]
                            }
                        ) as response:
                            if response.status != 200:
                                continue

                            data = await response.json()
                            jury_details = data.get("result")

                            if not jury_details or "verdict" not in jury_details or jury_details.get("verdict") in [-1, None]:
                                continue

                            # Обновляем информацию в базе данных
                            await self.db.juries.update_one(
                                {"juryid": jury["juryid"]},
                                {
                                    "$set": {
                                        "verdict": jury_details["verdict"],
                                        "votes": jury["vote_count"],
                                    }
                                }
                            )

                await asyncio.sleep(60)

            except Exception as e:
                log.error(f"Ошибка при получении деталей жюри: {e}")
                await asyncio.sleep(10)

    """Получение дополнительной информации о жюри"""
    async def discover_details(self, jury: Jury):
        try:
            # TODO: Получение дополнительной информации о жюри
            pass
        except Exception as e:
            log.error(f"Ошибка при получении дополнительной информации о жюри: {e}")

    """Получение адреса активного узла из базы данных"""
    async def get_active_node_instance(self) -> Optional[Node]:
        try:
            if not self.node is None:
                return self.node
            
            node = await self.db.nodes.find_one(
                {"public": True, "version": {"$gte": "0.22.14"}},
                sort=[("update", -1)]
            )

            return Node.from_dict(node)
        except Exception as e:
            log.error(f"Ошибка при получении активного узла: {e}")
            return None
