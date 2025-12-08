# ПРЕОБРАЗОВАНИЕ ФОРМАТА ПРОВАЙДЕРА
from typing import Dict, Any
import logging

from app.models.appeal_model import AppealDetailResponse, TransactionRequisite
from app.models.card_models.out_card_transaction_model import OutCardTransactionResponse
from app.models.other_models import InfoTransactionResponse
from app.models.card_models.in_card_transaction_internal_bank_model import InInternalCardTransactionResponse
from app.models.card_models.in_card_transaction_model import InCardTransactionResponse
from app.models.qr_and_sim_models.in_qr_transaction_model import InQrTransactionResponse
from app.models.qr_and_sim_models.in_sim_transaction_model import InSimTransactionResponse
from app.models.sbp_models.in_sbp_transaction_model import InSbpTransactionResponse
from app.models.sbp_models.in_sbp_transaction_model_iternal import InInternalSbpTransactionResponse
from app.models.sbp_models.out_sbp_transaction_model import OutSbpTransactionResponse

logger = logging.getLogger(__name__)


# Преобразование формата провайдера (PayIn | Карта)
def transform_from_provider_format_card_in(provider_response: Dict[str, Any]) -> InCardTransactionResponse:
    try:
        return InCardTransactionResponse(
            id=provider_response["id"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            expires_at=provider_response["expires_at"],
            amount=provider_response["amount"],
            currency=provider_response["currency"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"],
            card_number=provider_response["card_number"],
            owner_name=provider_response["owner_name"],
            bank_name=provider_response["bank_name"],
            country_name=provider_response["country_name"],
            payment_currency=provider_response["payment_currency"],
            payment_link=provider_response["payment_link"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")


# Преобразование формата провайдера (PayIn | Карта (внутрибанк))
def transform_from_provider_format_card_internal_in(provider_response: Dict[str, Any]) -> InInternalCardTransactionResponse:
    try:
        return InInternalCardTransactionResponse(
            id=provider_response["id"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            expires_at=provider_response["expires_at"],
            amount=provider_response["amount"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"],
            phone_number=provider_response["phone_number"],
            owner_name=provider_response["owner_name"],
            bank_name=provider_response["bank_name"],
            country_name=provider_response["country_name"],
            payment_currency=provider_response["payment_currency"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")


# Преобразование формата провайдера (PayIn | СБП)
def transform_from_provider_format_sbp_in(provider_response: Dict[str, Any]) -> InSbpTransactionResponse:
    try:
        return InSbpTransactionResponse(
            id=provider_response["id"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            expires_at=provider_response["expires_at"],
            amount=provider_response["amount"],
            currency=provider_response["currency"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"],
            phone_number=provider_response["phone_number"],
            owner_name=provider_response["owner_name"],
            bank_name=provider_response["bank_name"],
            country_name=provider_response["country_name"],
            payment_currency=provider_response["payment_currency"],
            payment_link=provider_response["payment_link"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")


# Преобразование формата провайдера (PayIn | СБП (внутрибанк))
def transform_from_provider_format_sbp_internal_in(provider_response: Dict[str, Any]) -> InInternalSbpTransactionResponse:
    try:
        return InInternalSbpTransactionResponse(
            id=provider_response["id"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            expires_at=provider_response["expires_at"],
            amount=provider_response["amount"],
            currency=provider_response["currency"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"],
            phone_number=provider_response["phone_number"],
            owner_name=provider_response["owner_name"],
            bank_name=provider_response["bank_name"],
            country_name=provider_response["country_name"],
            payment_currency=provider_response["payment_currency"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")


# Преобразование формата провайдера (PayIn | QR НСПК)
def transform_from_provider_format_qr_in(provider_response: Dict[str, Any]) -> InQrTransactionResponse:
    try:
        return InQrTransactionResponse(
            id=provider_response["id"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            expires_at=provider_response["expires_at"],
            amount=provider_response["amount"],
            currency=provider_response["currency"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"],
            payment_url=provider_response["payment_url"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")


# Преобразование формата провайдера (PayIn | СИМ-карта)
def transform_from_provider_format_sim_in(provider_response: Dict[str, Any]) -> InSimTransactionResponse:
    try:
        return InSimTransactionResponse(
            id=provider_response["id"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            expires_at=provider_response["expires_at"],
            amount=provider_response["amount"],
            currency=provider_response["currency"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"],
            phone_number=provider_response["phone_number"],
            owner_name=provider_response["owner_name"],
            operator=provider_response["operator"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")


# Преобразование формата провайдера (Информация о платеже)
def transform_from_provider_format_info_in(provider_response: Dict[str, Any]) -> InfoTransactionResponse:
    try:
        return InfoTransactionResponse(
            id=provider_response["id"],
            created_at=provider_response["created_at"],
            updated_at=provider_response["updated_at"],
            expires_at=provider_response["expires_at"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            type=provider_response["type"],
            payment_method=provider_response["payment_method"],
            amount=provider_response["amount"],
            paid_amount=provider_response["paid_amount"],
            currency=provider_response["currency"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"],
            status=provider_response["status"],
            paid_at=provider_response["paid_at"],
            card_number=provider_response["card_number"],
            phone_number=provider_response["phone_number"],
            owner_name=provider_response["owner_name"],
            bank_name=provider_response["bank_name"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")


# Преобразование формата провайдера (PayOut | Карта)
def transform_from_provider_format_card_out(provider_response: Dict[str, Any]) -> OutCardTransactionResponse:
    try:
        return OutCardTransactionResponse(
            id=provider_response["id"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            expires_at=provider_response["expires_at"],
            amount=provider_response["amount"],
            currency=provider_response["currency"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")


# Преобразование формата провайдера (PayOut | СБП)
def transform_from_provider_format_spb_out(provider_response: Dict[str, Any]) -> OutSbpTransactionResponse:
    try:
        return OutSbpTransactionResponse(
            id=provider_response["id"],
            merchant_transaction_id=provider_response["merchant_transaction_id"],
            expires_at=provider_response["expires_at"],
            amount=provider_response["amount"],
            currency=provider_response["currency"],
            currency_rate=provider_response["currency_rate"],
            amount_in_usd=provider_response["amount_in_usd"],
            rate=provider_response["rate"],
            commission=provider_response["commission"]
        )
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе провайдера: {e}")
        raise ValueError(f"Неверный формат ответа провайдера: Отсутствует поле {e}")
