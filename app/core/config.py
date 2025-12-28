# КОНФИГУРАЦИЯ
from typing import Dict, Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_base_url: str = "http://localhost:8000"

    # Токен мерчанта в нашем API
    merchant_token: str = "test_token"

    # Провайдеры
    providers: Dict[str, Dict[str, Any]] = {
        "garex": {
            "base_url": f"https://stage.garex.one/default",
            "api_key": "provider_test_key"
        }
    }

    debug: bool = True

    # Настройки вебхуков
    webhook_enabled: bool = True
    webhook_secret_key: str = "test_secret_key_123"
    webhook_base_url: str = f"{api_base_url}/api/v1/webhooks/transaction"

    # URL приложения для формирования подписи
    base_webhook_url: str = "http://localhost:8000"


    class Config:
        env_file = "set.env"
        case_sensitive = False


# Создание объекта класса Settings
settings = Settings()
