# СЕРВИС ДЛЯ РАБОТЫ С ПРОВАЙДЕРОМ
import httpx
import logging
import json
from typing import Dict, Any

from app.api.tool_for_provider_service.transform_from_provider_format import (
    transform_from_provider_format_card,
    transform_from_provider_format_card_internal,
    transform_from_provider_format_sbp,
    transform_from_provider_format_sbp_internal,
    transform_from_provider_format_qr,
    transform_from_provider_format_sim,
    transform_from_provider_format_info
)
from app.api.tool_for_provider_service.transform_to_provider_format import (
    transform_to_provider_format_card,
    transform_to_provider_format_card_internal
)
from app.core.config import settings
from app.models.card_models.card_transaction_internal_bank_model import (
    InternalCardTransactionRequest,
    InternalCardTransactionResponse
)
from app.models.card_models.card_transaction_model import (
    CardTransactionRequest,
    CardTransactionResponse
)
from app.models.qr_and_sim_models.qr_transaction_model import QrTransactionResponse
from app.models.qr_and_sim_models.sim_transaction_model import SimTransactionResponse
from app.models.sbp_models.sbp_transaction_model import SbpTransactionResponse
from app.models.sbp_models.sbp_transaction_model_iternal import InternalSbpTransactionResponse
from app.models.other_models import InfoTransactionResponse

logger = logging.getLogger(__name__)


def _format_error_response(
        code: str,
        message: str,
) -> Dict[str, Any]:
    """
    Форматирование ошибки в соответствии с ТЗ

    Args:
        code: Код ошибки
        message: Сообщение об ошибке

    Returns:
        Dict: Отформатированный ответ об ошибке
    """
    error_response = {
        "code": code,
        "message": message
    }

    return error_response


def _transform_provider_error_status(error: httpx.HTTPStatusError) -> Exception:
    """
    Обработка HTTP ошибок от провайдера (4xx, 5xx)

    Args:
        error: httpx.HTTPStatusError

    Returns:
        Exception: Содержит отформатированный ответ об ошибке
    """
    try:
        error_data = error.response.json()
        status_code = error.response.status_code

        error_message = error_data.get('message', error.response.text)
        error_response = _format_error_response(
            code=str(status_code),
            message=error_message
        )

        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)

    except Exception:
        # Если не удалось распарсить JSON
        status_code = error.response.status_code
        error_response = _format_error_response(
            code=str(status_code),
            message=error.response.text
        )

        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)


def _transform_provider_error_request(error: httpx.RequestError) -> Exception:
    """
    Обработка ошибок запроса к провайдеру (сети, таймауты, соединение)

    Args:
        error: httpx.RequestError

    Returns:
        Exception: Содержит отформатированный ответ об ошибке
    """
    # Определяем тип ошибки
    if isinstance(error, httpx.ConnectTimeout):
        error_type = "Таймаут подключения"
    elif isinstance(error, httpx.ReadTimeout):
        error_type = "Таймаут чтения ответа"
    elif isinstance(error, httpx.WriteTimeout):
        error_type = "Таймаут отправки запроса"
    elif isinstance(error, httpx.ConnectError):
        error_type = "Ошибка подключения к серверу"
    elif isinstance(error, httpx.PoolTimeout):
        error_type = "Таймаут ожидания свободного соединения"
    elif isinstance(error, httpx.ReadError):
        error_type = "Ошибка чтения данных"
    elif isinstance(error, httpx.WriteError):
        error_type = "Ошибка записи данных"
    else:
        error_type = "Сетевая ошибка"

    # Формируем сообщение об ошибке
    error_response = _format_error_response(
        code="503",
        message=f"{error_type} при обращении к провайдеру"
    )

    error_message = json.dumps(error_response, ensure_ascii=False)
    return Exception(error_message)


def transform_provider_error(error: Exception) -> Exception:
    """
    Универсальная функция трансформации ошибок провайдера

    Args:
        error: Любое исключение

    Returns:
        Exception: Содержит отформатированный ответ об ошибке в JSON
    """
    if isinstance(error, httpx.HTTPStatusError):
        return _transform_provider_error_status(error)
    elif isinstance(error, httpx.RequestError):
        return _transform_provider_error_request(error)
    else:
        # Для других ошибок
        error_response = _format_error_response(
            code="500",
            message=str(error) if str(error) else "Неизвестная ошибка провайдера"
        )

        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)


# Обращение к серверу провайдера
class ProviderService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )

    async def create_card_transaction(self, request: CardTransactionRequest) -> CardTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру на создание карточной транзакции: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получен ответ от провайдера на создание карточной транзакции: {provider_data}')

            return transform_from_provider_format_card(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при создании карточной транзакции: {str(e)}')
            raise transform_provider_error(e)

    async def create_card_transaction_internal(self,
                                               request: InternalCardTransactionRequest) -> InternalCardTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_internal(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру на создание внутренней карточной транзакции: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получен ответ от провайдера на создание внутренней карточной транзакции: {provider_data}')

            return transform_from_provider_format_card_internal(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при создании внутренней карточной транзакции: {str(e)}')
            raise transform_provider_error(e)

    async def create_card_transaction_transgran(self,
                                                request: CardTransactionRequest) -> InternalCardTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(
                f'Отправка запроса провайдеру на создание трансграничной карточной транзакции: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получен ответ от провайдера на создание трансграничной карточной транзакции: {provider_data}')

            return transform_from_provider_format_card_internal(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при создании трансграничной карточной транзакции: {str(e)}')
            raise transform_provider_error(e)

    async def create_spb_transaction(self,
                                     request: CardTransactionRequest) -> SbpTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру на создание СБП транзакции: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получен ответ от провайдера на создание СБП транзакции: {provider_data}')

            return transform_from_provider_format_sbp(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при создании СБП транзакции: {str(e)}')
            raise transform_provider_error(e)

    async def create_spb_transaction_internal(self,
                                              request: InternalCardTransactionRequest) -> InternalSbpTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_internal(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру на создание внутренней СБП транзакции: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получен ответ от провайдера на создание внутренней СБП транзакции: {provider_data}')

            return transform_from_provider_format_sbp_internal(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при создании внутренней СБП транзакции: {str(e)}')
            raise transform_provider_error(e)

    async def create_spb_transaction_transgran(self,
                                               request: CardTransactionRequest) -> InternalSbpTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру на создание трансграничной СБП транзакции: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получен ответ от провайдера на создание трансграничной СБП транзакции: {provider_data}')

            return transform_from_provider_format_sbp_internal(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при создании трансграничной СБП транзакции: {str(e)}')
            raise transform_provider_error(e)

    async def create_qr_transaction(self,
                                    request: CardTransactionRequest) -> QrTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру на создание QR транзакции: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получен ответ от провайдера на создание QR транзакции: {provider_data}')

            return transform_from_provider_format_qr(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при создании QR транзакции: {str(e)}')
            raise transform_provider_error(e)

    async def create_sim_transaction(self,
                                     request: CardTransactionRequest) -> SimTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру на создание SIM транзакции: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получен ответ от провайдера на создание SIM транзакции: {provider_data}')

            return transform_from_provider_format_sim(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при создании SIM транзакции: {str(e)}')
            raise transform_provider_error(e)

    async def cancel_transaction(self, transaction_id: str) -> None | bool | Exception:
        try:
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса на отмену транзакции {transaction_id}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/{transaction_id}/cancel',
                headers=headers
            )

            if response.status_code == 204:
                logger.info(f'Транзакция {transaction_id} успешно отменена')
                return True
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Transaction should be in progress.')

                    # Форматируем ошибку отмены
                    error_response = _format_error_response(
                        code="400",
                        message=error_message
                    )

                    error_message_json = json.dumps(error_response, ensure_ascii=False)
                    raise Exception(error_message_json)

                except Exception:
                    error_response = _format_error_response(
                        code="400",
                        message="Transaction should be in progress."
                    )

                    error_message_json = json.dumps(error_response, ensure_ascii=False)
                    raise Exception(error_message_json)
            else:
                response.raise_for_status()

        except Exception as e:
            logger.error(f'Ошибка при отмене транзакции {transaction_id}: {str(e)}')
            raise Exception(transform_provider_error(e))

    async def get_transaction_info(self, transaction_id: str) -> InfoTransactionResponse:
        try:
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Запрос информации о транзакции {transaction_id}')
            response = await self.client.get(
                f'{settings.provider_base_url}/transactions/{transaction_id}',
                headers=headers
            )

            if response.status_code == 404:
                error_response = _format_error_response(
                    code="404",
                    message=f"Транзакция {transaction_id} не найдена"
                )

                error_message = json.dumps(error_response, ensure_ascii=False)
                raise Exception(error_message)

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f'Получена информация о транзакции {transaction_id}')

            return transform_from_provider_format_info(provider_data)

        except Exception as e:
            logger.error(f'Ошибка при запросе информации о транзакции {transaction_id}: {str(e)}')
            raise transform_provider_error(e)

    async def close(self):
        await self.client.aclose()


provider_service = ProviderService()