# РОУТЕРЫ
from fastapi import APIRouter

from app.api.routers import webhook_router
from app.api.routers.cancel_transaction_router import router as cancel_router
from app.main import app

# Основной роутер
main_router = APIRouter()

# Подключение остальных роутеров
app.include_router(cancel_router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(webhook_router, prefix="/api/v1/transactions/", tags=["webhooks"])
