# МОДЕЛИ ДАННЫХ (PayIn | Карта)
import re

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal, InvalidOperation  # Точный десятичный тип данных

from app.api.resources.valid_res import valid_res


class InCardTransactionRequest(BaseModel):
    # Обязательные поля
    amount: str = Field(..., min_length=1, description="Сумма заявки")
    currency: str = Field(..., min_length=1, description="ISO код валюты")
    merchant_transaction_id: str = Field(..., min_length=1, description="Идентификатор платежа")
    # Поля для уникализации
    auto_amount_limit: Optional[int] = Field(default=0, ge=0, le=20, description="Количество шагов для подбора")
    auto_amount_step: Optional[int] = Field(default=1, ge=1, description="Размер шага при подборе")
    # Опциональные поля
    currency_rate: Optional[str] = Field(None, description="Курс валюты")
    client_id: Optional[str] = Field(None, description="Идентификатор клиента")

    @field_validator("amount")  # Валидация поля amount
    @classmethod
    def validate_amount(csl, value: str) -> str:
        try:
            amount = Decimal(value)
            if not re.match(r"^\d+$", value.strip()):
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

    @field_validator("currency_rate") # Валидация поля currency_rate
    @classmethod
    def validate_currency_rate(csl, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        try:
            currency_rate = Decimal(value)
            if currency_rate <= 0:
                raise ValueError("Поле currency_rate должно быть положительным числом")
        except (ValueError, InvalidOperation):
            raise ValueError("Неправильный формат поля currency_rate")
        return value


class InCardTransactionResponse(BaseModel):
    id: int  # Идентификатор платежа в системе провайдера
    merchant_transaction_id: str  # Идентификатор платежа в системе мерчанта
    expires_at: datetime  # Срок действия платежа
    amount: str  # Сумма транзакции
    currency: str  # Валюта
    currency_rate: str  # Курс валюты
    amount_in_usd: str  # Сумма транзакции в USD
    rate: str  # Тариф
    commission: str  # Коммисия
    card_number: str  # Номер счета
    owner_name: str  # Владелец счета
    bank_name: str  # Название банка
    country_name: str  # Название страны банка
    payment_currency: str  # Код валюты оплаты
    payment_link: str  # Редирект
