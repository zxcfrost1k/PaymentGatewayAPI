# СЕРВИС ДЛЯ РАБОТЫ С ПРОВАЙДЕРОМ
import httpx
import logging
import json
from typing import Dict, Any, Optional, List
from fastapi import UploadFile

from app.api.tool_for_provider_service.transform_from_provider_format import (
    transform_from_provider_format_card_in,
    transform_from_provider_format_card_internal_in,
    transform_from_provider_format_sbp_in,
    transform_from_provider_format_sbp_internal_in,
    transform_from_provider_format_qr_in,
    transform_from_provider_format_sim_in,
    transform_from_provider_format_info_in,
    transform_from_provider_format_card_out,
    transform_from_provider_format_spb_out
)
from app.api.tool_for_provider_service.transform_to_provider_format import (
    transform_to_provider_format_card_in,
    transform_to_provider_format_card_internal_in,
    transform_to_provider_format_card_out,
    transform_to_provider_format_sbp_out
)
from app.models.appeal_model import (
    AppealCreateResponse,
    AppealCreateRequest,
    AppealDetailResponse,
    TransactionRequisite
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
from app.models.sbp_models.out_sbp_transaction_model import (
    OutSbpTransactionRequest,
    OutSbpTransactionResponse
)
from app.models.qr_and_sim_models.in_qr_transaction_model import InQrTransactionResponse
from app.models.qr_and_sim_models.in_sim_transaction_model import InSimTransactionResponse
from app.models.sbp_models.in_sbp_transaction_model import InSbpTransactionResponse
from app.models.sbp_models.in_sbp_transaction_model_iternal import InInternalSbpTransactionResponse
from app.models.other_models import InfoTransactionResponse, BalanceResponse, LimitsResponse, LimitItem
from app.core.config import settings
from app.api.resources.valid_res import valid_res


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


# Преобразование ответа провайдера в нашу модель лимитов
def _transform_limits_response(provider_data: dict) -> LimitsResponse:
    try:
        logger.info(f"Преобразование ответа провайдера: {provider_data}")

        # Создаем словарь для лимитов
        limits_dict = {}

        # 1. Обрабатываем CARD
        if "card" in provider_data and isinstance(provider_data["card"], dict):
            card_data = provider_data["card"]
            if "min_amount" in card_data and "max_amount" in card_data:
                limits_dict["card"] = LimitItem(
                    min_amount=str(card_data["min_amount"]),
                    max_amount=str(card_data["max_amount"])
                )

        # 2. Обрабатываем SBP
        if "sbp" in provider_data and isinstance(provider_data["sbp"], dict):
            sbp_data = provider_data["sbp"]
            if "min_amount" in sbp_data and "max_amount" in sbp_data:
                limits_dict["sbp"] = LimitItem(
                    min_amount=str(sbp_data["min_amount"]),
                    max_amount=str(sbp_data["max_amount"])
                )

        # 3. Обрабатываем QR
        if "qr" in provider_data and isinstance(provider_data["qr"], dict):
            qr_data = provider_data["qr"]
            if "min_amount" in qr_data and "max_amount" in qr_data:
                limits_dict["qr"] = LimitItem(
                    min_amount=str(qr_data["min_amount"]),
                    max_amount=str(qr_data["max_amount"])
                )

        # 4. Обрабатываем SIM
        if "sim" in provider_data and isinstance(provider_data["sim"], dict):
            sim_data = provider_data["sim"]
            if "min_amount" in sim_data and "max_amount" in sim_data:
                limits_dict["sim"] = LimitItem(
                    min_amount=str(sim_data["min_amount"]),
                    max_amount=str(sim_data["max_amount"])
                )

        # Создаем финальный объект
        result = LimitsResponse(**limits_dict)
        logger.info(f"Преобразование завершено успешно")
        return result

    except KeyError as e:
        logger.error(f"Ключевая ошибка при преобразовании лимитов: {str(e)}")
        logger.error(f"Ответ провайдера: {provider_data}")
        raise transform_provider_error(e)

    except Exception as e:
        logger.error(f"Неожиданная ошибка при преобразовании лимитов: {str(e)}")
        logger.error(f"Тип ошибки: {type(e).__name__}")
        import traceback
        logger.error(f"Трассировка: {traceback.format_exc()}")
        raise transform_provider_error(e)


# Обращение к серверу провайдера
def _transform_appeal_response(provider_data: dict) -> AppealDetailResponse:
    try:
        # Преобразуем requisite если есть
        requisite_data = provider_data.get("transaction_requisite", {})
        transaction_requisite = TransactionRequisite(
            bank=requisite_data.get("bank"),
            card=requisite_data.get("card"),
            owner=requisite_data.get("owner"),
            country_name=requisite_data.get("country_name")
        )

        return AppealDetailResponse(
            id=provider_data["id"],
            created_at=provider_data["created_at"],
            status=provider_data["status"],
            amount=provider_data["amount"],
            appeal_cancel_reason_name=provider_data.get("appeal_cancel_reason_name"),
            transaction_id=provider_data["transaction_id"],
            merchant_transaction_id=provider_data["merchant_transaction_id"],
            transaction_created_at=provider_data["transaction_created_at"],
            transaction_amount=provider_data.get("transaction_amount"),
            transaction_paid_amount=provider_data["transaction_paid_amount"],
            transaction_requisite=transaction_requisite,
            transaction_currency_code=provider_data["transaction_currency_code"]
        )

    except KeyError as e:
        logger.error(f"Отсутствует обязательное поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: отсутствует поле {e}")


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

    # Получение баланса
    async def get_balance(self) -> BalanceResponse:
        try:
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info("Отправка запроса провайдеру на баланс")

            # В режиме отладки - заглушка
            if settings.debug:
                return BalanceResponse(
                    balance="100.00",
                    currency_rate="90.32"
                )

            # Реальный запрос к провайдеру
            response = await self.client.get(
                f"{settings.provider_base_url}/api/v1/balance",
                headers=headers
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на баланс: {provider_data}")

            return BalanceResponse(
                balance=provider_data["balance"],
                currency_rate=provider_data["currency_rate"]
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при запросе баланса: {e.response.status_code}")
            raise transform_provider_error(e)
        except Exception as e:
            logger.error(f"Ошибка при получении баланса: {str(e)}")
            raise transform_provider_error(e)

    # Получение лимитов
    async def get_limits(self, currency_code: str) -> LimitsResponse:
        try:
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Запрос лимитов для валюты: {currency_code}")

            # В режиме отладки возвращаем заглушку
            if settings.debug:
                logger.info("Режим DEBUG - возвращаем тестовые данные лимитов")
                return _transform_limits_response({
                    "card": {
                        "min_amount": "100",
                        "max_amount": "200000"
                    },
                    "sbp": {
                        "min_amount": "100",
                        "max_amount": "200000"
                    }
                })

            # Реальный запрос к провайдеру
            response = await self.client.get(
                f"{settings.provider_base_url}/api/v1/limits/{currency_code}",
                headers=headers
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ лимитов от провайдера: {provider_data}")

            return _transform_limits_response(provider_data)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при запросе лимитов: {e.response.status_code}")
            raise transform_provider_error(e)
        except Exception as e:
            logger.error(f"Ошибка при получении лимитов: {str(e)}")
            raise transform_provider_error(e)

    # Создание апелляции
    async def create_appeal(
            self,
            request: AppealCreateRequest,
            files: List[UploadFile]
    ) -> AppealCreateResponse:
        try:
            logger.info(f"Создание апелляции для транзакции {request.transaction_id}")

            # Формируем данные для multipart/form-data
            form_data = {"amount": request.amount, "transaction_id": request.transaction_id}

            # Создаем multipart данные
            data = {}
            files_data = []

            # Добавляем текстовые поля
            for key, value in form_data.items():
                data[key] = value

            # Добавляем файлы
            for i, file in enumerate(files):
                # Читаем содержимое файла
                file_content = await file.read()

                # Проверяем размер файла
                if len(file_content) > settings.max_file_size:
                    raise Exception(f"Файл {file.filename} превышает максимальный размер: {settings.max_file_size}")

                content_type = file.content_type or "application/octet-stream"
                if content_type not in valid_res.valid_file_types:
                    raise Exception(f"Неподдерживаемый тип файла: {content_type}")

                # Добавляем файл в список
                files_data.append(
                    ("attachments", (file.filename, file_content, content_type))
                )

                # Сбрасываем позицию чтения файла
                await file.seek(0)

            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}"
            }

            logger.info(
                f"Отправка запроса провайдеру на создание апелляции:"
                f" transaction_id={request.transaction_id},"
                f" amount={request.amount}")

            # Отправляем запрос с файлами
            response = await self.client.post(
                f"{settings.provider_base_url}/api/v1/appeals/",
                headers=headers,
                data=data,
                files=files_data
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на создание апелляции: {provider_data}")

            return AppealCreateResponse(id=provider_data["id"])

        except Exception as e:
            logger.error(f"Ошибка при создании апелляции: {str(e)}")
            raise transform_provider_error(e)

    # Получение информации об апелляции
    async def get_appeal_info(self, appeal_id: int) -> AppealDetailResponse:
        try:
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Запрос информации об апелляции {appeal_id}")

            # Реальный запрос к провайдеру
            response = await self.client.get(
                f"{settings.provider_base_url}/api/v1/appeals/{appeal_id}",
                headers=headers
            )

            if response.status_code == 404:
                error_response = _create_error_response(
                    code="404",
                    message=f"Апелляция {appeal_id} не найдена"
                )
                error_message = json.dumps(error_response, ensure_ascii=False)
                raise Exception(error_message)

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получена информация об апелляции {appeal_id}")

            return _transform_appeal_response(provider_data)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при запросе апелляции {appeal_id}: {e.response.status_code}")
            raise transform_provider_error(e)
        except Exception as e:
            logger.error(f"Ошибка при получении информации об апелляции {appeal_id}: {str(e)}")
            raise transform_provider_error(e)

    # Преобразование формата провайдера (Просмотр апелляций)

    # Выход из приложения
    async def close(self):
        await self.client.aclose()


# Создание объекта класса ProviderService
provider_service = ProviderService()
