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

@router.post("/list_nodes")
async def post_nodes():
    # Получение списка узлов
    nodes = [ Node.from_dict(doc) for doc in db.nodes.find({}) ]
    # Получение списка пиров
    peers = [ Peer.from_dict(doc) for doc in db.peers.find({}) ]

    for node in nodes:
        node.peers = []
        for peer in peers:
            if ( peer.address_node if node.public else peer.address ) == node.address:
                node.peers.append(peer)

    # Форматирование списка узлов для возврата в формате JSON
    return [node.to_dict() for node in nodes]

@router.get("/nodes")
async def get_nodes():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(current_dir, "../www/nodes.html"))