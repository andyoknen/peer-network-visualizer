import os
from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from models.node import Node
from models.peer import Peer
from services.helpers import config
from fastapi.responses import FileResponse

router = APIRouter()

# Создание клиента MongoDB с использованием конфигурации
client = MongoClient(config['mongodb']['uri'])
db = client[config['mongodb']['database']]

# Сначала создайте индексы (выполнить один раз при настройке БД):
db.peers.create_index("address")
db.peers.create_index("address_node")

@router.post("/list_nodes")
async def list_nodes():
    nodes = []
    # Используем Unix timestamp для фильтрации
    for doc in db.nodes.find():
        peer_count = db.peers.count_documents({
            "$or": [
                {"address": doc["address"]},
                {"address_node": doc["address"]}
            ]
        })
        doc["peer_count"] = peer_count
        nodes.append(Node.from_dict(doc))

    return [node.to_dict() for node in nodes]

# @router.get("/nodes")
# async def nodes():
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     return FileResponse(os.path.join(current_dir, "../www/nodes.html"))

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