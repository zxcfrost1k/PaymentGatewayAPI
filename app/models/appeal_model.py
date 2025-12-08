# МОДЕЛИ ДАННЫХ (Апелляции)
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
import re
from decimal import Decimal, InvalidOperation


# Модель для создания апелляций
class AppealCreateRequest(BaseModel):
    transaction_id: str = Field(..., min_length=1, description="Идентификатор транзакции")
    amount: str = Field(..., min_length=1, description="Сумма апелляции")

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


class AppealCreateResponse(BaseModel):
    id: int  # Идентификатор апелляции в системе провайдера


# Модель для реквизитов транзакции
class TransactionRequisite(BaseModel):
    bank: Optional[str] = Field(None, description="Банк")
    card: Optional[str] = Field(None, description="Номер карты")
    owner: Optional[str] = Field(None, description="Владелец счета")
    country_name: Optional[str] = Field(None, description="Название страны")


# Модель для просмотра апелляции
class AppealDetailResponse(BaseModel):
    id: int = Field(..., description="Идентификатор апелляции")
    created_at: datetime = Field(..., description="Дата создания апелляции")
    status: str = Field(..., description="Статус апелляции")
    amount: str = Field(..., description="Сумма апелляции")
    appeal_cancel_reason_name: Optional[str] = Field(None, description="Причина отмены апелляции")
    transaction_id: int = Field(..., description="Идентификатор транзакции")
    merchant_transaction_id: str = Field(..., description="Идентификатор транзакции в системе мерчанта")
    transaction_created_at: datetime = Field(..., description="Дата создания транзакции")
    transaction_amount: Optional[str] = Field(None, description="Сумма транзакции")
    transaction_paid_amount: str = Field(..., description="Фактическая оплаченная сумма")
    transaction_requisite: TransactionRequisite = Field(..., description="Реквизиты транзакции")
    transaction_currency_code: str = Field(..., description="Код валюты транзакции")
