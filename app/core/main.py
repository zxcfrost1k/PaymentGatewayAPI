# ОСНОВНОЕ ПРИЛОЖЕНИЕ
import logging

from fastapi import status as http_status
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request, Depends, Header

from app.api.security.auth import security
from app.api.resources.providers_resources import providers_res
from app.models.paygatecore.pay_in_model import PayInRequest
from app.models.paygatecore.pay_in_bank_model import PayInBankRequest
from app.api.services.provider_services.garex_service.webhook_router import router as webhook_router
from app.models.paygatecore.pay_out_model import PayOutRequest, PayOutRequest2

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Инициализация приложения
app = FastAPI(
    title="Payment API Gateway",
    description="Сервис трансляции API между нашей системой и провайдером",
    version="1.0"
)


# Подключение роутеров
app.include_router(webhook_router, prefix="/api/v1/webhooks", tags=["webhooks"])


# Создание ответа об ошибке
def _create_error_response(code: str,
                           message: str,
                           errors: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
    error_response: Dict[str, Any] = {
        "code": code,
        "message": message
    }

    # Поле errors только при множественных ошибках
    if errors and len(errors) > 1:
        error_response["errors"] = errors

    return error_response


# Обработчик HTTP исключений
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if "/webhook" in str(request.url.path):
        # Для вебхуков - простой формат с кодом ошибки и сообщением
        error_detail = {
            "error": str(exc.detail) if isinstance(exc.detail, str) else "Webhook processing error",
            "status": "error"
        }

        # Если детали уже в нужном формате
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            error_detail = exc.detail

        return JSONResponse(
            status_code=exc.status_code,
            content=error_detail
        )
    else:
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            # Уже структурированная ошибка
            error_detail = exc.detail
        else:
            # Простое сообщение - преобразуем в структурированное
            error_detail = _create_error_response(
                code=str(exc.status_code),
                message=str(exc.detail)
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_detail
        )


# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors: Dict[str, List[str]] = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        if not field:
            field = ".".join(str(loc) for loc in error["loc"])
        field = field.replace("body.", "")

        if field not in errors:
            errors[field] = []

        if error["type"] == "missing":
            errors[field].append("Пропущено обязательное поле")
        else:
            error_msg = error.get("msg", "Некорректное значение")
            errors[field].append(error_msg)

    # Определяем, нужно ли показывать errors
    total_errors = sum(len(error_list) for error_list in errors.values())

    # Одна ошибка - показываем только code и message
    if total_errors == 1:
        first_field = next(iter(errors))
        first_error = errors[first_field][0]
        return JSONResponse(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_create_error_response(
                code="422",
                message=first_error
            )
        )
    # Множественные ошибки - показываем code, message и errors
    else:
        return JSONResponse(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_create_error_response(
                code="422",
                message="Ошибка валидации данных",
                errors=errors
            )
        )


# Обработчик непредвиденных ошибок
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_create_error_response(
            code="500",
            message="Внутренняя ошибка сервера"
        )
    )


# Эндпоинт проверки здоровья приложения
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Домашняя страница API
@app.get("/")
async def root():
    return {"message": "Payment API Gateway is running"}


# PayIn | Карта
@app.post("/api/v1/transactions/card", tags=["payin"])
async def pay_in_card(
        request: PayInRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: card")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_in_card(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: card")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayIn | Карта (внутрибанк)
@app.post("/api/v1/transactions/internal-card", tags=["payin"])
async def pay_in_internal_card(
        request: PayInBankRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: internal-card")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_in_internal_card(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: internal-card")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayIn | Карта (трансгран)
@app.post("/api/v1/transactions/transgran-card", tags=["payin"])
async def pay_in_transgran_card(
        request: PayInRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: transgran-card")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_in_transgran_card(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: transgran-card")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayIn | СБП
@app.post("/api/v1/transactions/sbp", tags=["payin"])
async def pay_in_sbp(
        request: PayInRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: sbp")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_in_sbp(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: sbp")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayIn | СБП (внутрибанк)
@app.post("/api/v1/transactions/internal-sbp", tags=["payin"])
async def pay_in_internal_sbp(
        request: PayInBankRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: internal-sbp")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_in_internal_sbp(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: internal-sbp")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayIn | СБП (трансгран)
@app.post("/api/v1/transactions/transgran-sbp", tags=["payin"])
async def pay_in_transgran_sbp(
        request: PayInRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: transgran-sbp")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_in_transgran_sbp(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: transgran-sbp")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayIn | QR НСПК
@app.post("/api/v1/transactions/qr", tags=["payin"])
async def pay_in_qr(
        request: PayInRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: qr")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_in_qr(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: qr")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayIn | СИМ-карта
@app.post("/api/v1/transactions/sim", tags=["payin"])
async def pay_in_sim(
        request: PayInRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: sim")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_in_sim(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: sim")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayOut | Карта
@app.post("/api/v1/transactions/payout-card", tags=["payout"])
async def pay_out_card(
        request: PayOutRequest,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating out transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: card")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_out_card(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating out transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: card")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# PayOut | СБП
@app.post("/api/v1/transactions/payout-sbp", tags=["payout"])
async def pay_out_sbp(
        request: PayOutRequest2,
        provider_name: str = Header(..., alias="Provider-data"),
        token: str = Depends(security)
):
    try:
        logger.info(f"Creating out transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: sbp")

        try:
            provider = providers_res.PROVIDERS[provider_name]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Провайдер не найден в системе"
            )

        pay_in_provider = await provider.pay_out_sbp(request)
        return pay_in_provider

    except HTTPException as e:
        logger.info(f"Error with creating out transaction: "
                    f"{request.merchant_transaction_id} on provider: {provider_name} "
                    f"via method: sbp")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


# Запуск приложения
if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting API Gateway...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
