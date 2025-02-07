import os
from fastapi import APIRouter, HTTPException, Body
from pymongo import MongoClient
from models.node import Node
from models.peer import Peer
from models.jury import Jury
from services.helpers import config
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import ClassVar

router = APIRouter()

# Создание клиента MongoDB с использованием конфигурации
client = MongoClient(config['mongodb']['uri'])
db = client[config['mongodb']['database']]

# Сначала создайте индексы (выполнить один раз при настройке БД):
db.peers.create_index("address")
db.peers.create_index("address_node")

class ListNodesRequest(BaseModel):
    public: bool = False
    count: int = 0

@router.post("/list_nodes")
async def list_nodes(request: ListNodesRequest = Body(default=None)):
    nodes = []
    
    if request is not None:
        query = {"public": True} if request.public else {}
        cursor = db.nodes.find(query)
        if request.count > 0:
            cursor = cursor.limit(request.count)
    else:
        cursor = db.nodes.find()
    
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

@router.post("/list_juries")
async def list_juries(request: ListJuriesRequest = Body(default=None)):
    skip = request.page * request.limit
    
    cursor = db.juries.find().sort("height", -1 if request.desc else 1).skip(skip).limit(request.limit)
    juries = []
    
    for jury in cursor:
        juries.append(Jury.from_dict(jury))
        
    total = db.juries.count_documents({})
    
    return {
        "items": [jury.to_dict() for jury in juries],
        "total": total,
        "page": request.page,
        "limit": request.limit
    }

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
        raise HTTPException(status_code=404, detail="Файл не найден")