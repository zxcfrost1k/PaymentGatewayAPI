# Проверка подписи вебхука
from fastapi import Request, HTTPException
import json

from app.core.config import settings
from app.api.services.provider_services.our.signature_service import verify_signature


async def verify_webhook_signature(request: Request):
    if not settings.webhook_enabled:
        raise HTTPException(
            status_code=403,
            detail="Webhook now: turn off"
        )

    if not settings.webhook_secret_key:
        raise HTTPException(
            status_code=500,
            detail="No secret key provided"
        )

    # Получение тела запроса
    try:
        body_bytes = await request.body()
        request_body = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid format: JSON"
        )

    # Получение подписи из заголовка
    signature_header = request.headers.get("X-Signature")
    if not signature_header:
        raise HTTPException(
            status_code=401,
            detail="No signature provided"
        )

    # Получение полного URL запроса
    full_url = str(request.url)

    # Проверка подписи
    if not verify_signature(full_url, request_body, signature_header, settings.webhook_secret_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    return request_body
