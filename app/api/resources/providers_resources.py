# ПЕРЕНАПРВЛЕНИЕ ПРОВАЙДЕРОВ
from app.api.services.provider_services.garex_service.garex import garex


class ProvidersResource:
    PROVIDERS = {
        "garex": garex
    }


providers_res = ProvidersResource
