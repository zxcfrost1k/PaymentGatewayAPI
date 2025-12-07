# ПРЕОБРАЗОВАНИЕ ФОРМАТА ПРОВАЙДЕРА
from typing import Dict, Any

import logging

from app.models.other_models import InfoTransactionResponse

logger = logging.getLogger(__name__)

from app.models.card_models.card_transaction_internal_bank_model import InternalCardTransactionResponse
from app.models.card_models.card_transaction_model import CardTransactionResponse
from app.models.qr_and_sim_models.qr_transaction_model import QrTransactionResponse
from app.models.qr_and_sim_models.sim_transaction_model import SimTransactionResponse
from app.models.sbp_models.sbp_transaction_model import SbpTransactionResponse
from app.models.sbp_models.sbp_transaction_model_iternal import InternalSbpTransactionResponse


def transform_from_provider_format_card(provider_response: Dict[str, Any]) -> CardTransactionResponse:
    try:
        return CardTransactionResponse(
            id=provider_response['id'],
            merchant_transaction_id=provider_response['merchant_transaction_id'],
            expires_at=provider_response['expires_at'],
            amount=provider_response['amount'],
            currency=provider_response['currency'],
            currency_rate=provider_response['currency_rate'],
            amount_in_usd=provider_response['amount_in_usd'],
            rate=provider_response['rate'],
            commission=provider_response['commission'],
            card_number=provider_response['card_number'],
            owner_name=provider_response['owner_name'],
            bank_name=provider_response['bank_name'],
            country_name=provider_response['country_name'],
            payment_currency=provider_response['payment_currency'],
            payment_link=provider_response['payment_link']
        )
    except KeyError as e:
        logger.error(f'Отсутствует ожидаемое поле в ответе провайдера: {e}')
        raise ValueError(f'Неверный формат ответа провайдера: Отсутствует поле {e}')


def transform_from_provider_format_card_internal(provider_response: Dict[str, Any]) -> InternalCardTransactionResponse:
    try:
        return InternalCardTransactionResponse(
            id=provider_response['id'],
            merchant_transaction_id=provider_response['merchant_transaction_id'],
            expires_at=provider_response['expires_at'],
            amount=provider_response['amount'],
            currency_rate=provider_response['currency_rate'],
            amount_in_usd=provider_response['amount_in_usd'],
            rate=provider_response['rate'],
            commission=provider_response['commission'],
            phone_number=provider_response['phone_number'],
            owner_name=provider_response['owner_name'],
            bank_name=provider_response['bank_name'],
            country_name=provider_response['country_name'],
            payment_currency=provider_response['payment_currency']
        )
    except KeyError as e:
        logger.error(f'Отсутствует ожидаемое поле в ответе провайдера: {e}')
        raise ValueError(f'Неверный формат ответа провайдера: Отсутствует поле {e}')


def transform_from_provider_format_sbp(provider_response: Dict[str, Any]) -> SbpTransactionResponse:
    try:
        return SbpTransactionResponse(
            id=provider_response['id'],
            merchant_transaction_id=provider_response['merchant_transaction_id'],
            expires_at=provider_response['expires_at'],
            amount=provider_response['amount'],
            currency=provider_response['currency'],
            currency_rate=provider_response['currency_rate'],
            amount_in_usd=provider_response['amount_in_usd'],
            rate=provider_response['rate'],
            commission=provider_response['commission'],
            phone_number=provider_response['phone_number'],
            owner_name=provider_response['owner_name'],
            bank_name=provider_response['bank_name'],
            country_name=provider_response['country_name'],
            payment_currency=provider_response['payment_currency'],
            payment_link=provider_response['payment_link']
        )
    except KeyError as e:
        logger.error(f'Отсутствует ожидаемое поле в ответе провайдера: {e}')
        raise ValueError(f'Неверный формат ответа провайдера: Отсутствует поле {e}')


def transform_from_provider_format_sbp_internal(provider_response: Dict[str, Any]) -> InternalSbpTransactionResponse:
    try:
        return InternalSbpTransactionResponse(
            id=provider_response['id'],
            merchant_transaction_id=provider_response['merchant_transaction_id'],
            expires_at=provider_response['expires_at'],
            amount=provider_response['amount'],
            currency=provider_response['currency'],
            currency_rate=provider_response['currency_rate'],
            amount_in_usd=provider_response['amount_in_usd'],
            rate=provider_response['rate'],
            commission=provider_response['commission'],
            phone_number=provider_response['phone_number'],
            owner_name=provider_response['owner_name'],
            bank_name=provider_response['bank_name'],
            country_name=provider_response['country_name'],
            payment_currency=provider_response['payment_currency']
        )
    except KeyError as e:
        logger.error(f'Отсутствует ожидаемое поле в ответе провайдера: {e}')
        raise ValueError(f'Неверный формат ответа провайдера: Отсутствует поле {e}')


def transform_from_provider_format_qr(provider_response: Dict[str, Any]) -> QrTransactionResponse:
    try:
        return QrTransactionResponse(
            id=provider_response['id'],
            merchant_transaction_id=provider_response['merchant_transaction_id'],
            expires_at=provider_response['expires_at'],
            amount=provider_response['amount'],
            currency=provider_response['currency'],
            currency_rate=provider_response['currency_rate'],
            amount_in_usd=provider_response['amount_in_usd'],
            rate=provider_response['rate'],
            commission=provider_response['commission'],
            payment_url=provider_response['payment_url']
        )
    except KeyError as e:
        logger.error(f'Отсутствует ожидаемое поле в ответе провайдера: {e}')
        raise ValueError(f'Неверный формат ответа провайдера: Отсутствует поле {e}')


def transform_from_provider_format_sim(provider_response: Dict[str, Any]) -> SimTransactionResponse:
    try:
        return SimTransactionResponse(
            id=provider_response['id'],
            merchant_transaction_id=provider_response['merchant_transaction_id'],
            expires_at=provider_response['expires_at'],
            amount=provider_response['amount'],
            currency=provider_response['currency'],
            currency_rate=provider_response['currency_rate'],
            amount_in_usd=provider_response['amount_in_usd'],
            rate=provider_response['rate'],
            commission=provider_response['commission'],
            phone_number=provider_response['phone_number'],
            owner_name=provider_response['owner_name'],
            operator=provider_response['operator']
        )
    except KeyError as e:
        logger.error(f'Отсутствует ожидаемое поле в ответе провайдера: {e}')
        raise ValueError(f'Неверный формат ответа провайдера: Отсутствует поле {e}')


def transform_from_provider_format_info(provider_response: Dict[str, Any]) -> InfoTransactionResponse:
    try:
        return InfoTransactionResponse(
            id=provider_response['id'],
            created_at=provider_response['created_at'],
            updated_at=provider_response['updated_at'],
            expires_at=provider_response['expires_at'],
            merchant_transaction_id=provider_response['merchant_transaction_id'],
            type=provider_response['type'],
            payment_method=provider_response['payment_method'],
            amount=provider_response['amount'],
            paid_amount=provider_response['paid_amount'],
            currency=provider_response['currency'],
            currency_rate=provider_response['currency_rate'],
            amount_in_usd=provider_response['amount_in_usd'],
            rate=provider_response['rate'],
            commission=provider_response['commission'],
            status=provider_response['status'],
            paid_at=provider_response['paid_at'],
            card_number=provider_response['card_number'],
            phone_number=provider_response['phone_number'],
            owner_name=provider_response['owner_name'],
            bank_name=provider_response['bank_name']
        )
    except KeyError as e:
        logger.error(f'Отсутствует ожидаемое поле в ответе провайдера: {e}')
        raise ValueError(f'Неверный формат ответа провайдера: Отсутствует поле {e}')
