from models.node import Node

class MetricsCollector:
    def __init__(self, mongodb_client):
        self.db = mongodb_client

    async def store_metrics(self, node_info: Node):
        # Сохранение метрик узла в MongoDB
        # Агрегация статистики
        pass