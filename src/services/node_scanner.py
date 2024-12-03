from models.node import Node

class NodeScanner:
    def __init__(self, config):
        self.rpc_port = config['rpc_port']
        self.timeout = config['timeout']

    async def scan_node(self, ip: str) -> Node:
        # Проверка доступности узла
        # Сбор информации через RPC API:
        # - версия
        # - высота блока
        # - количество пиров
        # - загрузка сети
        pass