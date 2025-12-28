# ИНСТРУМЕНТЫ ПРОВАЙДЕРА GAREX
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Dict, Any

from app.api.resources.garex_resources.bank_resources import bank_res
from app.core.config import settings
from app.models.paygatecore.pay_in_bank_model import (
    PayInBankRequest,
    PayInBankResponse,
    PayInBankResponse2
)
from app.models.paygatecore.pay_in_model import (
    PayInRequest,
    PayInResponse,
    PayInResponse2
)
from app.models.paygatecore.pay_out_model import PayOutRequest, PayOutRequest2, PayOutResponse
from app.models.paygatecore.pay_in_sim_model import PayInSimResponse


def _get_country(bank_code: str) -> str:
    if bank_code in bank_res.BANKS_RUS:
        return "РФ"
    elif bank_code in bank_res.BANKS_AZN:
        return "Азербайджан"
    elif bank_code in bank_res.BANKS_ABH:
        return "Абхазия"
    else:
        return "Таджикистан"


def transform_to_provider_format(request: PayInRequest, method: str) -> Dict[str, Any]:
    payload = {
        "orderId": request.merchant_transaction_id,
        "merchantId": settings.merchant_token,
        "method": method,
        "amount": int(request.amount),
        "currency": request.currency,
        "user_id": "??",
        "callbackUri": settings.webhook_base_url
    }
    return payload


def transform_to_provider_format_with_bank(request: PayInBankRequest, method: str, bank_code: str) -> Dict[str, Any]:
    payload = {
        "orderId": request.merchant_transaction_id,
        "merchantId": settings.merchant_token,
        "method": method,
        "assetOrBank": bank_code,
        "amount": int(request.amount),
        "currency": request.currency,
        "user_id": "??",
        "callbackUri": settings.webhook_base_url
    }
    return payload


def transform_to_provider_format_for_out(request: PayOutRequest, method: str) -> Dict[str, Any]:
    payload = {
        "orderId": request.merchant_transaction_id,
        "merchantId": settings.merchant_token,
        "method": method,
        "assetOrBank": "??",
        "requisiteNumber": request.card_number,
        "requisiteRecipient": request.owner_name,
        "amount": int(request.amount),
        "currency": request.currency,
        "callbackUri": settings.webhook_base_url
    }
    return payload


def transform_to_provider_format_for_out_2(request: PayOutRequest2, method: str, bank_code: str) -> Dict[str, Any]:
    payload = {
        "orderId": request.merchant_transaction_id,
        "merchantId": settings.merchant_token,
        "method": method,
        "assetOrBank": bank_code,
        "requisiteNumber": request.phone_number,
        "requisiteRecipient": request.owner_name,
        "amount": int(request.amount),
        "currency": request.currency,
        "callbackUri": settings.webhook_base_url
    }
    return payload


def transform_from_provider_format(provider_response: Dict[str, Any]) -> PayInResponse:
    try:
        return PayInResponse(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            card_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            bank_name=provider_response["result"]["bankName"],
            country_name=_get_country(provider_response["result"]["bank"]),
            payment_currency="RUB",
            payment_link=provider_response["url"]
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_2(provider_response: Dict[str, Any]) -> PayInResponse2:
    try:
        return PayInResponse2(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes=10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            card_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            bank_name=provider_response["result"]["bankName"],
            country_name=_get_country(provider_response["result"]["bank"]),
            payment_currency="RUB"
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_3(provider_response: Dict[str, Any]) -> PayInSimResponse:
    try:
        return PayInSimResponse(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            phone_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            operator=provider_response["result"]["bankName"]
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_with_bank(provider_response: Dict[str, Any]) -> PayInBankResponse:
    try:
        return PayInBankResponse(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            phone_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            bank_name=provider_response["result"]["bankName"],
            country_name=_get_country(provider_response["result"]["bank"]),
            payment_currency="RUB",
            payment_link=provider_response["url"]
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_with_bank_2(provider_response: Dict[str, Any]) -> PayInBankResponse2:
    try:
        return PayInBankResponse2(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            phone_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            bank_name=provider_response["result"]["bankName"],
            country_name=_get_country(provider_response["result"]["bank"]),
            payment_currency="RUB"
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_for_out(provider_response: Dict[str, Any]) -> PayOutResponse:
    try:
        return PayOutResponse(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"])
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )
