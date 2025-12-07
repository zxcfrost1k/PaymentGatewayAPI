# ОСНОВНОЕ ПРИЛОЖЕНИЕ
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Dict, List, Optional, Any
from fastapi import Request

from app.api.services.provider_service import provider_service
from app.models.card_models.in_card_transaction_internal_bank_model import InInternalCardTransactionRequest
from app.models.card_models.in_card_transaction_model import InCardTransactionRequest
from app.models.card_models.out_card_transaction_model import OutCardTransactionRequest
from app.models.other_models import ErrorResponse
from app.models.sbp_models.out_sbp_transaction_model import OutSbpTransactionRequest

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Инициализация приложения
app = FastAPI(
    title="Payment API Gateway",
    description="Сервис трансляции API между нашей системой и провайдером",
    version="1.0"
)


# Создание ответа об ошибке
def _create_error_response(code: str,
                           message: str,
                           errors: Optional[Dict[str,
                           List[str]]] = None) -> Dict[str, Any]:
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_create_error_response(
                code="422",
                message=first_error
            )
        )
    # Множественные ошибки - показываем code, message и errors
    else:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
@app.post("/api/v1/transactions/card")
async def create_card_transaction_in(
        request: InCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction: {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 12345,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "9.65",
            "rate": "10",
            "commission": "0.48",
            "card_number": "1234123412344321",
            "owner_name": "Дмитрий Н.",
            "bank_name": "Альфа-Банк",
            "country_name": "РФ",
            "payment_currency": "RUB",
            "payment_link": "https://example.com/payment-link"
        }

    except Exception as e:
        logger.error(f"Error creating (in) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании транзакции"
            )
        )


# PayIn | Карта (внутрибанк)
@app.post("/api/v1/transactions/internal-card")
async def create_card_transaction_internal_in(
        request: InInternalCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction: {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 12345,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency_rate": "103.67",
            "amount_in_usd": "9.65",
            "rate": "10",
            "commission": "0.48",
            "phone_number": "79204563423",
            "owner_name": "Дима",
            "bank_name": request.bank_name,
            "country_name": "РФ",
            "payment_currency": "RUB"
        }

    except Exception as e:
        logger.error(f"Error creating (in) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании транзакции"
            )
        )


# PayIn | Карта (трансгран)
@app.post("/api/v1/transactions/transgran-card")
async def create_card_transaction_transgran_card_in(
        request: InCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction: {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 12345,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "9.65",
            "rate": "10",
            "commission": "0.48",
            "phone_number": "79204563423",
            "owner_name": "Дима",
            "bank_name": "ВТБ",
            "country_name": "РФ",
            "payment_currency": "RUB"
        }

    except Exception as e:
        logger.error(f"Error creating (in) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании транзакции"
            )
        )


# PayIn | СБП
@app.post("/api/v1/transactions/sbp")
async def create_sbp_transaction_in(
        request: InCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction: {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 12345,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "9.65",
            "rate": "10",
            "commission": "0.48",
            "phone_number": "79204563423",
            "owner_name": "Дима",
            "bank_name": "ВТБ",
            "country_name": "РФ",
            "payment_currency": "RUB",
            "payment_link": "https://example.com/payment-link"
        }

    except Exception as e:
        logger.error(f"Error creating (in) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании транзакции"
            )
        )


# PayIn | СБП (внутрибанк)
@app.post("/api/v1/transactions/internal-sbp")
async def create_sbp_transaction_internal_in(
        request: InInternalCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction: {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 12345,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "9.65",
            "rate": "10",
            "commission": "0.48",
            "phone_number": "79204563423",
            "owner_name": "Дима",
            "bank_name": "ВТБ",
            "country_name": "РФ",
            "payment_currency": "RUB"
        }

    except Exception as e:
        logger.error(f"Error creating (in) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании транзакции"
            )
        )


# PayIn | СБП (трансгран)
@app.post("/api/v1/transactions/transgran-sbp")
async def create_sbp_transaction_transgran_in(
        request: InCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction: {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 12345,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "9.65",
            "rate": "10",
            "commission": "0.48",
            "phone_number": "79204563423",
            "owner_name": "Дима",
            "bank_name": "ВТБ",
            "country_name": "РФ",
            "payment_currency": "RUB"
        }

    except Exception as e:
        logger.error(f"Error creating (in) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании транзакции"
            )
        )


# PayIn | QR НСПК
@app.post("/api/v1/transactions/qr")
async def create_qr_transaction_in(
        request: InCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction: {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 1496256,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "0.96",
            "rate": "10",
            "commission": "0.48",
            "payment_url": "https://qr.nspk.ru/GJSKDFHGJKSDHFJHSDKSDFJFHJSDHF?type=01&bank=100000000004&crc=13DD"
        }

    except Exception as e:
        logger.error(f"Error creating (in) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании транзакции"
            )
        )


# PayIn | СИМ-карта
@app.post("/api/v1/transactions/sim")
async def create_sim_transaction_in(
        request: InCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction: {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 1496256,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "0.96",
            "rate": "10",
            "commission": "0.48",
            "phone_number": "+79861231212",
            "owner_name": "Дима",
            "operator": "Мегафон"
        }

    except Exception as e:
        logger.error(f"Error creating (in) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании транзакции"
            )
        )


# PayOut | Карта
@app.post("/api/v1/transactions/payout-card")
async def create_card_transaction_out(
        request: OutCardTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction (out): {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 12345,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "9.65",
            "rate": "10",
            "commission": "0.48",
        }

    except Exception as e:
        logger.error(f"Error creating (out) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании вывода"
            )
        )


# PayOut | СБП
@app.post("/api/v1/transactions/payout-spb")
async def create_sbp_transaction_out(
        request: OutSbpTransactionRequest
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        logger.info(f"Creating transaction (out): {request.merchant_transaction_id}")

        # Ответ провайдера на запрос (включить при выходе в прод)
        # result = await provider_service.create_card_transaction(request)

        # Временно возвращаем заглушку вместо вызова провайдера (удалить при выходе в прод)
        return {
            "id": 12345,
            "merchant_transaction_id": request.merchant_transaction_id,
            "expires_at": "2025-01-20T21:49:41.918607Z",
            "amount": request.amount,
            "currency": request.currency,
            "currency_rate": "103.67",
            "amount_in_usd": "9.65",
            "rate": "10",
            "commission": "0.48",
        }

    except Exception as e:
        logger.error(f"Error creating (out) transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code="500",
                message="Ошибка при создании вывода"
            )
        )


# PayIn | Отмена платежа
@app.post(
    "/transactions/{transaction_id}/cancel",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Transaction cancelled successfully"},
        400: {"model": ErrorResponse, "description": "Transaction cannot be cancelled"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def cancel_transaction(
        transaction_id: str,
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        await provider_service.cancel_transaction(transaction_id)
        return None  # 204 No Content

    except Exception as e:
        error_message = str(e)
        if "Transaction should be in progress" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    code="1",
                    message="Transaction should be in progress."
                )
            )
        else:
            # Для других ошибок провайдера
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=_create_error_response(
                    code=str(e).split("\"")[3],
                    message=str(e).split("\"")[-2]
                )
            )


# Информация о платеже
@app.post("/api/v1/transactions/{transaction_id}")
async def get_transaction_info(
        transaction_id: str,
        # token: str = Depends(security)  # Проверка токена авторизации (включить при выходе в прод)
):
    try:
        transaction_info = await provider_service.get_transaction_info(transaction_id)
        return transaction_info

    except Exception as e:
        logger.error(f"Error by get (in) transaction info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_create_error_response(
                code=str(e).split("\"")[3],
                message=str(e).split("\"")[-2]
            )
        )


# Запуск приложения
if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting API Gateway...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
