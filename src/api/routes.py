from fastapi import APIRouter
from pymongo import MongoClient
from models.node import Node
from models.peer import Peer
import yaml

router = APIRouter()

# Чтение конфигурации из файла
with open("config/config.yml", "r") as file:
    config = yaml.safe_load(file)

# Создание клиента MongoDB с использованием конфигурации
client = MongoClient(config['mongodb']['uri'])
db = client[config['mongodb']['database']]

@router.post("/nodes")
async def get_nodes():
    # Получение списка узлов
    nodes = [ Node.from_dict(doc) for doc in db.nodes.find({}) ]
    # Получение списка пиров
    peers = [ Peer.from_dict(doc) for doc in db.peers.find({}) ]

    for node in nodes:
        for peer in peers:
            if peer.address_node == node.address:
                node.peers.append(peer)

    # Форматирование списка узлов для возврата в формате JSON
    return [node.to_dict() for node in nodes]

@router.post("/metrics")
async def get_metrics():
    # Получение агрегированной статистики сети
    pass