import asyncio
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from api.routes import router
from services.peer_discovery import PeerDiscovery
from services.jury_discovery import JuryDiscovery
from services.helpers import config

# Контекст-менеджер для FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация подключения к MongoDB
    mongodb_client = AsyncIOMotorClient(config['mongodb']['uri'])

    # Инициализация сервисов
    # app.state.peer_discovery = PeerDiscovery(mongodb_client[config['mongodb']['database']], config['initial_peers'])
    app.state.jury_discovery = JuryDiscovery(mongodb_client[config['mongodb']['database']])
    
    # Запуск фоновых процессов
    # asyncio.create_task(app.state.peer_discovery.discover())
    asyncio.create_task(app.state.jury_discovery.discover())

    yield
    
    # Закрытие подключений при завершении
    mongodb_client.close()

# Создание FastAPI приложения
app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="")

# Запуск приложения
if __name__ == "__main__":
    # Запуск фоновых сервисов
    uvicorn.run(
        app, 
        host=config['fastapi']['host'], 
        port=config['fastapi']['port'],
        log_level=config['logging'].get('level', 'info')
    )
    
