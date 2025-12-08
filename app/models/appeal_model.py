# МОДЕЛИ ДАННЫХ (Апелляции)
from pydantic import BaseModel, Field, field_validator
import re
from decimal import Decimal, InvalidOperation


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
