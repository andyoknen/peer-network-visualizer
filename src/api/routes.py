import os
from fastapi import APIRouter
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
    # Затем используйте простой подсчет для каждого узла
    nodes = []
    for doc in db.nodes.find({}):
        peer_count = db.peers.count_documents({
            "$or": [
                {"address": doc["address"]},
                {"address_node": doc["address"]}
            ]
        })
        doc["peer_count"] = peer_count
        nodes.append(Node.from_dict(doc))

    # Форматирование списка узлов для возврата в формате JSON
    return [node.to_dict() for node in nodes]

@router.get("/nodes")
async def nodes():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(current_dir, "../www/nodes.html"))