from fastapi import APIRouter

router = APIRouter()

@router.post("/nodes")
async def get_nodes():
    # Получение списка активных узлов
    pass

@router.post("/metrics")
async def get_metrics():
    # Получение агрегированной статистики сети
    pass