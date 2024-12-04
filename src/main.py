import asyncio
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import yaml
from contextlib import asynccontextmanager
from api.routes import router
from services.peer_discovery import PeerDiscovery


# Настройка логирования
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Загрузка конфигурации
def load_config():
    with open('config/config.yml', 'r') as f:
        return yaml.safe_load(f)
    
config = load_config()

# Контекст-менеджер для FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация подключения к MongoDB
    mongodb_client = AsyncIOMotorClient(config['mongodb']['uri'])
    
    # Инициализация сервисов
    peer_discovery = PeerDiscovery(mongodb_client[config['mongodb']['database']], config['initial_peers'])
    
    # Сохраняем сервисы в состоянии приложения
    app.state.peer_discovery = peer_discovery

    asyncio.create_task(app.state.peer_discovery.discover_peers())
    
    yield
    
    # Закрытие подключений при завершении
    mongodb_client.close()

# Создание FastAPI приложения
app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api/v1")

# Запуск приложения
if __name__ == "__main__":

    # Запуск фоновых сервисов
    uvicorn.run(app, host=config['fastapi']['host'], port=config['fastapi']['port'])
    
