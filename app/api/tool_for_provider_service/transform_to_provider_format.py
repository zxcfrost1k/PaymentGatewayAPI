# ПРЕОБРАЗОВАНИЕ ЗАПРОСА В ФОРМАТ ПРОВАЙДЕРА
from typing import Dict, Any

from app.models.card_models.in_card_transaction_internal_bank_model import InInternalCardTransactionRequest
from app.models.card_models.in_card_transaction_model import InCardTransactionRequest
from app.models.card_models.out_card_transaction_model import OutCardTransactionRequest
from app.models.sbp_models.out_sbp_transaction_model import OutSbpTransactionRequest


# Преобразование запроса в формат провайдера (PayIn | Карта)
def transform_to_provider_format_card_in(request: InCardTransactionRequest) -> Dict[str, Any]:
    payload = {
        "amount": request.amount,
        "currency": request.currency,
        "merchant_transaction_id": request.merchant_transaction_id,
        "rate": request.rate,
        "currency_rate": request.currency_rate,
        "client_id": request.client_id
    }

    payload = {k: v for k, v in payload.items() if v is not None}  # Убираем None значения
    return payload


# Преобразование запроса в формат провайдера (PayIn | Карта (внутрибанк))
def transform_to_provider_format_card_internal_in(request: InInternalCardTransactionRequest) -> Dict[str, Any]:
    payload = {
        "amount": request.amount,
        "currency": request.currency,
        "merchant_transaction_id": request.merchant_transaction_id,
        "bank_name": request.bank_name,
        "rate": request.rate,
        "currency_rate": request.currency_rate,
        "client_id": request.client_id
    }

    payload = {k: v for k, v in payload.items() if v is not None}  # Убираем None значения
    return payload


# Преобразование запроса в формат провайдера (PayOut | Карта)
def transform_to_provider_format_card_out(request: OutCardTransactionRequest) -> Dict[str, Any]:
    payload = {
        "amount": request.amount,
        "currency": request.currency,
        "card_number": request.card_number,
        "owner_name": request.owner_name,
        "merchant_transaction_id": request.merchant_transaction_id
    }

    return payload


# Преобразование запроса в формат провайдера (PayOut | СБП)
def transform_to_provider_format_sbp_out(request: OutSbpTransactionRequest) -> Dict[str, Any]:
    payload = {
        "amount": request.amount,
        "currency": request.currency,
        "phone_number": request.phone_number,
        "bank_id": request.bank_id,
        "owner_name": request.owner_name,
        "merchant_transaction_id": request.merchant_transaction_id
    }

    return payload
