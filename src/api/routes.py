import os
from fastapi import APIRouter, HTTPException, Body
from pymongo import MongoClient
from models.node import Node
from models.peer import Peer
from models.jury import Jury
from services.helpers import config
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from typing import ClassVar
from aiohttp import ClientSession

router = APIRouter()

client = MongoClient(config['mongodb']['uri'])
db = client[config['mongodb']['database']]

db.peers.create_index("address")
db.peers.create_index("address_node")

db.juries.create_index([
    ("id", "text"),
    ("address", "text"),
    ("content_id", "text")
])

### Static files
@router.get("/{filename:path}")
async def serve_static(filename: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, "../www")
    
    # Добавляем .html только если в имени файла нет точки
    extension = ".html" if "." not in filename else ""
    file_path = os.path.join(base_dir, filename + extension)
    
    # Проверяем, что итоговый путь находится внутри base_dir
    try:
        real_path = os.path.realpath(file_path)
        if not real_path.startswith(os.path.realpath(base_dir)):
            raise HTTPException(status_code=403, detail="Доступ запрещен")
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный путь")
        
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return RedirectResponse(url="/index", status_code=302)


### API
class ListNodesRequest(BaseModel):
    public: bool = False
    count: int = 0

@router.post("/list_nodes")
async def list_nodes(request: ListNodesRequest = Body(default=None)):
    nodes = []
    
    query = {}

    query["height"] = {"$gt": 0}

    if request and request.public:
        query["public"] = True
        
    cursor = db.nodes.find(query)
    if request and request.count > 0:
        cursor = cursor.limit(request.count)
    
    for doc in cursor:
        peer_count = db.peers.count_documents({
            "$or": [
                {"address": doc["address"]},
                {"address_node": doc["address"]}
            ]
        })
        doc["peer_count"] = peer_count
        nodes.append(Node.from_dict(doc))

    return [node.to_dict() for node in nodes]


class ListJuriesRequest(BaseModel):
    page: int = 0
    limit: int = 10
    desc: bool = True
    verdict: int = -2
    search: str = ""
@router.post("/list_juries")
async def list_juries(request: ListJuriesRequest = Body(default=None)):
    skip = request.page * request.limit
    
    filter = {} # -2 - все, 0 - оправданные, 1 - осужденные, -1 - в процессе
    if request.verdict != -2:
        filter["verdict"] = request.verdict

    if request.search:
        filter["$text"] = {"$search": request.search}

    cursor = db.juries.find(filter).sort("height", -1 if request.desc else 1).skip(skip).limit(request.limit)
    juries = []
    
    for jury in cursor:
        juries.append(Jury.from_dict(jury))
        
    total = db.juries.count_documents(filter)
    
    return {
        "items": [jury.to_dict() for jury in juries],
        "total": total,
        "page": request.page,
        "limit": request.limit
    }


@router.post("/jury_moderators/{jury_id}")
async def get_jury_moderators(jury_id: str):
    try:
        # Получаем активную ноду
        node = db.nodes.find_one(
            {"public": True, "version": {"$gte": "0.22.14"}},
            sort=[("update", -1)]
        )
        
        if not node:
            raise HTTPException(status_code=404, detail="Активная нода не найдена")
        
        # Отправляем запрос на получение модераторов
        async with ClientSession() as session:
            async with session.post(
                f"http://{node['address']}:38081/rpc/public",
                json={
                    "method": "getjurymoderators",
                    "params": [jury_id]
                }
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Ошибка получения модераторов")
                    
                data = await response.json()
                return data.get("result", [])
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
