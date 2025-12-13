# МОДЕЛИ ДАННЫХ (PayOut | СБП)
import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from decimal import Decimal, InvalidOperation  # Точный десятичный тип данных

from app.api.resources.valid_res import valid_res


class OutSbpTransactionRequest(BaseModel):
    # Обязательные поля
    amount: str = Field(..., min_length=1, description="Сумма заявки")
    currency: str = Field(..., min_length=1, description="ISO код валюты")
    phone_number: str = Field(..., min_length=1, description="Номер телефона")
    bank_id: str = Field(..., min_length=1, description="Номер банка")
    owner_name: str = Field(..., min_length=1, description="ФИО владельца карты")
    merchant_transaction_id: str = Field(..., min_length=1, description="Идентификатор платежа")

    @field_validator("amount")  # Валидация поля amount
    @classmethod
    def validate_amount(csl, value: str) -> str:
        try:
            amount = Decimal(value)
            if not re.match(r"^\d+$", value):
                raise ValueError("Поле amount должно быть целым числом")
            if amount <= 0:
                raise ValueError("Поле amount должно быть положительным числом")
            if value.startswith("0"):
                raise ValueError("Неправильный формат поля amount")
        except (ValueError, InvalidOperation):
            raise ValueError("Неправильный формат поля amount")
        return value

    @field_validator("currency")  # Валидация поля currency
    @classmethod
    def validate_currency(csl, value: str) -> str:
        if value in valid_res.valid_currency:
            return value
        raise ValueError("Неправильный формат поля currency")

    @field_validator("phone_number")  # Валидация поля phone_number
    @classmethod
    def validate_phone_number(csl, value: str) -> str:
        if re.match(r"^\d+$", value) and len(value) > 10:
            return value
        raise ValueError("Неправильный формат поля phone_number")


class OutSbpTransactionResponse(BaseModel):
    id: int  # Идентификатор платежа в системе провайдера
    merchant_transaction_id: str  # Идентификатор платежа в системе мерчанта
    expires_at: datetime  # Срок действия платежа
    amount: str  # Сумма транзакции
    currency: str  # Валюта
    currency_rate: str  # Курс валюты
    amount_in_usd: str  # Сумма транзакции в USD
    rate: str  # Тариф
    commission: str  # Коммисия
