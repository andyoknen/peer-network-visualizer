from fastapi import APIRouter

router = APIRouter()

@router.get("/nodes")
async def get_nodes():
    # Получение списка активных узлов
    pass

@router.get("/metrics")
async def get_metrics():
    # Получение агрегированной статистики сети
    pass