# СЕРВИС ДЛЯ РАБОТЫ С ПРОВАЙДЕРОМ
import httpx
import logging
import json
from typing import Dict, Any, Optional, List

from app.api.tool_for_provider_service.transform_from_provider_format import (
    transform_from_provider_format_card_in,
    transform_from_provider_format_card_internal_in,
    transform_from_provider_format_sbp_in,
    transform_from_provider_format_sbp_internal_in,
    transform_from_provider_format_qr_in,
    transform_from_provider_format_sim_in,
    transform_from_provider_format_info_in,
    transform_from_provider_format_card_out, transform_from_provider_format_spb_out
)
from app.api.tool_for_provider_service.transform_to_provider_format import (
    transform_to_provider_format_card_in,
    transform_to_provider_format_card_internal_in,
    transform_to_provider_format_card_out, transform_to_provider_format_sbp_out
)
from app.models.card_models.in_card_transaction_internal_bank_model import (
    InInternalCardTransactionRequest,
    InInternalCardTransactionResponse
)
from app.models.card_models.in_card_transaction_model import (
    InCardTransactionRequest,
    InCardTransactionResponse,
)
from app.models.card_models.out_card_transaction_model import (
    OutCardTransactionRequest,
    OutCardTransactionResponse
)
from app.models.qr_and_sim_models.in_qr_transaction_model import InQrTransactionResponse
from app.models.qr_and_sim_models.in_sim_transaction_model import InSimTransactionResponse
from app.models.sbp_models.in_sbp_transaction_model import InSbpTransactionResponse
from app.models.sbp_models.in_sbp_transaction_model_iternal import InInternalSbpTransactionResponse
from app.models.other_models import InfoTransactionResponse
from app.core.config import settings
from app.models.sbp_models.out_sbp_transaction_model import OutSbpTransactionRequest, OutSbpTransactionResponse

logger = logging.getLogger(__name__)


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


# Обработка HTTP ошибок от провайдера (4xx, 5xx)
def _transform_provider_error_status(error: httpx.HTTPStatusError) -> Exception:
    try:
        error_data = error.response.json()
        status_code = error.response.status_code

        error_message = error_data.get("message", error.response.text)
        error_response = _create_error_response(
            code=str(status_code),
            message=error_message
        )

        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)

    # Невалидный JSON
    except json.JSONDecodeError:
        status_code = error.response.status_code
        error_response = _create_error_response(
            code=str(status_code),
            message=error.response.text
        )
        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)

    # Нет нужных атрибутов или ключей
    except (AttributeError, KeyError):
        status_code = getattr(error.response, 'status_code', 500)
        text = getattr(error.response, 'text', str(error))

        error_response = _create_error_response(
            code=str(status_code),
            message=text
        )
        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)

    # Непредвиденные ошибки
    except Exception as e:
        # Лог с полным traceback
        logger.exception(f"Непредвиденная ошибка в _transform_provider_error_status")

        error_response = _create_error_response(
            code="500",
            message=f"Ошибка обработки ответа провайдера: {str(e)}"
        )
        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)


# Обработка ошибок запроса к провайдеру (сети, таймауты, соединение)
def _transform_provider_error_request(error: httpx.RequestError) -> Exception:
    # Определение типа ошибки
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

    # Формирование сообщения об ошибке
    error_response = _create_error_response(
        code="503",
        message=f"{error_type} при обращении к провайдеру"
    )

    error_message = json.dumps(error_response, ensure_ascii=False)
    return Exception(error_message)


# Универсальная функция обработки ошибок провайдера (для любых исключений)
def transform_provider_error(error: Exception) -> Exception:
    if isinstance(error, httpx.HTTPStatusError):
        return _transform_provider_error_status(error)
    elif isinstance(error, httpx.RequestError):
        return _transform_provider_error_request(error)
    # Для других ошибок
    else:
        error_response = _create_error_response(
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

    # PayIn | Карта
    async def create_card_transaction_in(self, request: InCardTransactionRequest) -> InCardTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_in(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание карточной транзакции: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/card",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание карточной транзакции: {provider_data}")

            return transform_from_provider_format_card_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании карточной транзакции: {str(e)}")
            raise transform_provider_error(e)

    # PayIn | Карта (внутрибанк)
    async def create_card_transaction_internal_in(self,
                                                  request: InInternalCardTransactionRequest)-> (
            InInternalCardTransactionResponse):
        try:
            provider_payload = transform_to_provider_format_card_internal_in(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание внутренней карточной транзакции: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/internal-card",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание внутренней карточной транзакции: {provider_data}")

            return transform_from_provider_format_card_internal_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании внутренней карточной транзакции: {str(e)}")
            raise transform_provider_error(e)

    # PayIn | Карта (трансгран)
    async def create_card_transaction_transgran_in(self,
                                                   request: InCardTransactionRequest) -> InInternalCardTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_in(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(
                f"Отправка запроса провайдеру на создание трансграничной карточной транзакции: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/transgran-card",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание трансграничной карточной транзакции: {provider_data}")

            return transform_from_provider_format_card_internal_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании трансграничной карточной транзакции: {str(e)}")
            raise transform_provider_error(e)

    # PayIn | СБП
    async def create_sbp_transaction_in(self,
                                        request: InCardTransactionRequest) -> InSbpTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_in(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание СБП транзакции: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/transactions/sbp",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание СБП транзакции: {provider_data}")

            return transform_from_provider_format_sbp_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании СБП транзакции: {str(e)}")
            raise transform_provider_error(e)

    # PayIn | СБП (внутрибанк)
    async def create_sbp_transaction_internal_in(self,
                                                 request: InInternalCardTransactionRequest) ->(
            InInternalSbpTransactionResponse):
        try:
            provider_payload = transform_to_provider_format_card_internal_in(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание внутренней СБП транзакции: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}transactions/internal-sbp",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание внутренней СБП транзакции: {provider_data}")

            return transform_from_provider_format_sbp_internal_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании внутренней СБП транзакции: {str(e)}")
            raise transform_provider_error(e)

    # PayIn | СБП (трансгран)
    async def create_sbp_transaction_transgran_in(self,
                                                  request: InCardTransactionRequest) -> InInternalSbpTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_in(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание трансграничной СБП транзакции: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/transgran-sbp",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание трансграничной СБП транзакции: {provider_data}")

            return transform_from_provider_format_sbp_internal_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании трансграничной СБП транзакции: {str(e)}")
            raise transform_provider_error(e)

    # PayIn | QR НСПК
    async def create_qr_transaction_in(self,
                                       request: InCardTransactionRequest) -> InQrTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_in(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание QR транзакции: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/qr",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание QR транзакции: {provider_data}")

            return transform_from_provider_format_qr_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании QR транзакции: {str(e)}")
            raise transform_provider_error(e)

    # PayIn | СИМ-карта
    async def create_sim_transaction_in(self,
                                        request: InCardTransactionRequest) -> InSimTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_in(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание SIM транзакции: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/sim",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание SIM транзакции: {provider_data}")

            return transform_from_provider_format_sim_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании SIM транзакции: {str(e)}")
            raise transform_provider_error(e)

    # PayIn | Отмена платежа
    async def cancel_transaction(self, transaction_id: str) -> None | bool | Exception:
        try:
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса на отмену транзакции {transaction_id}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/{transaction_id}/cancel",
                headers=headers
            )

            if response.status_code == 204:
                logger.info(f"Транзакция {transaction_id} успешно отменена")
                return True
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", "Transaction should be in progress.")

                    # Форматируем ошибку отмены
                    error_response = _create_error_response(
                        code="400",
                        message=error_message
                    )

                    error_message_json = json.dumps(error_response, ensure_ascii=False)
                    raise Exception(error_message_json)

                except Exception:
                    error_response = _create_error_response(
                        code="400",
                        message="Transaction should be in progress."
                    )

                    error_message_json = json.dumps(error_response, ensure_ascii=False)
                    raise Exception(error_message_json)
            else:
                response.raise_for_status()

        except Exception as e:
            logger.error(f"Ошибка при отмене транзакции {transaction_id}: {str(e)}")
            raise Exception(transform_provider_error(e))

    # Информация о платеже
    async def get_transaction_info(self, transaction_id: str) -> InfoTransactionResponse:
        try:
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Запрос информации о транзакции {transaction_id}")
            response = await self.client.get(
                f"{settings.provider_base_url}/api/v1/transactions/{transaction_id}",
                headers=headers
            )

            if response.status_code == 404:
                error_response = _create_error_response(
                    code="404",
                    message=f"Транзакция {transaction_id} не найдена"
                )

                error_message = json.dumps(error_response, ensure_ascii=False)
                raise Exception(error_message)

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получена информация о транзакции {transaction_id}")

            return transform_from_provider_format_info_in(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при запросе информации о транзакции {transaction_id}: {str(e)}")
            raise transform_provider_error(e)

    # PayOut | Карта
    async def create_card_transaction_out(self, request: OutCardTransactionRequest) -> OutCardTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_card_out(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание вывода на карту: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/payout-card",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание вывода на карту: {provider_data}")

            return transform_from_provider_format_card_out(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании вывода на карту: {str(e)}")
            raise transform_provider_error(e)

    # PayOut | СБП
    async def create_sbp_transaction_out(self, request: OutSbpTransactionRequest) -> OutSbpTransactionResponse:
        try:
            provider_payload = transform_to_provider_format_sbp_out(request)
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Отправка запроса провайдеру на создание вывода на карту по СБП: {provider_payload}")
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/transactions/payout-sbp",
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание вывода на карту по СБП: {provider_data}")

            return transform_from_provider_format_spb_out(provider_data)

        except Exception as e:
            logger.error(f"Ошибка при создании вывода на карту по СБП: {str(e)}")
            raise transform_provider_error(e)

    # Выход из приложения
    async def close(self):
        await self.client.aclose()


# Создание объекта класса ProviderService
provider_service = ProviderService()
