# КОНФИГУРАЦИЯ
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Настройки API
    api_base_url: str = "http://localhost:8000"

    # Токен мерчанта для аутентификации в нашем API
    merchant_token: str = "test_token_123"

    # Настройки провайдера
    provider_base_url: str = "http://localhost:8001"
    provider_api_key: str = "provider_test_key"

    debug: bool = True

    # Настройки вебхуков
    webhook_enabled: bool = True
    webhook_secret_key: str = "test_secret_key_123"

    # URL приложения для формирования подписи
    base_webhook_url: str = "http://localhost:8000"

    # Максимальный размер загружаемого файла
    max_file_size: int = 10 * 1024 * 1024 # (10 Мб)
    # Максимальное кол-во файлов во влажениях
    max_files_count: int = 10

    class Config:
        env_file = "../set.env"
        case_sensitive = False


# Создание объекта класса Settings
settings = Settings()
