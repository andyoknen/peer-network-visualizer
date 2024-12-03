import asyncio
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import yaml
from contextlib import asynccontextmanager
from api.routes import router
from services.node_scanner import NodeScanner
from services.peer_discovery import PeerDiscovery
from services.metrics_collector import MetricsCollector
from models.node import Node

# Настройка логирования
import logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Загрузка конфигурации
def load_config():
    with open('config/config.yml', 'r') as f:
        return yaml.safe_load(f)

# Фоновая задача для сканирования узлов
async def scan_nodes():
    while True:
        try:
            await app.state.peer_discovery.discover_peers()
            await asyncio.sleep(10)  # 5 минут
        except Exception as e:
            log.error(f"Ошибка при сканировании узлов: {e}")
            await asyncio.sleep(1)  # Ожидание 1 минута при ошибке

# Контекст-менеджер для FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация подключения к MongoDB
    config = load_config()
    mongodb_client = AsyncIOMotorClient(config['mongodb']['uri'])
    
    # Инициализация сервисов
    node_scanner = NodeScanner(config['scanner'])
    peer_discovery = PeerDiscovery(config['initial_peers'])
    metrics_collector = MetricsCollector(mongodb_client[config['mongodb']['database']])
    
    # Сохраняем сервисы в состоянии приложения
    app.state.node_scanner = node_scanner
    app.state.peer_discovery = peer_discovery
    app.state.metrics_collector = metrics_collector

    asyncio.create_task(scan_nodes())
    
    yield
    
    # Закрытие подключений при завершении
    await mongodb_client.close()

# Создание FastAPI приложения
app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api/v1")

# Запуск приложения
if __name__ == "__main__":

    # Запуск фоновых сервисов
    uvicorn.run(app, host="0.0.0.0", port=5000)
    
