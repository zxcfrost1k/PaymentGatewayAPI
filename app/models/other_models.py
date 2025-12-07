from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field



class CancelTransactionErrorResponse(BaseModel):
    code: int
    message: str


class ErrorResponse(BaseModel):
    code: Optional[str] = None
    message: str
    errors: Optional[Dict[str, List[str]]] = None


class PaginationParams(BaseModel):
    page_size: int = Field(default=10, ge=10, le=100)
    page_number: int = Field(default=1, ge=1)


class InfoTransactionResponse(BaseModel):
    id: int  # Идентификатор платежа в системе провайдера
    created_at: datetime  # Время создания платежа
    updated_at: datetime  # Время последнего изменения платежа
    expires_at: datetime  # Срок действия платежа
    merchant_transaction_id: str  # Идентификатор платежа в системе мерчанта
    type: str  # Тип транзакции (in/out)
    payment_method: str  # Способ оплаты (card, sbp, qr, sim)
    amount: str  # Сумма, на которую была создана транзакция
    paid_amount: str  # Сумма, на которую была выполнена оплата
    currency: str  # Валюта транзакции
    currency_rate: str  # Курс валюты на момент создания
    amount_in_usd: str  # Эквивалент суммы в USD
    rate: str  # Тариф мерчанта
    commission: str  # Комиссия мерчанта
    status: str  # Статус платежа
    paid_at: Optional[datetime] = None  # Время оплаты (может быть null)
    card_number: Optional[str] = None  # Номер карты (опционально)
    phone_number: Optional[str] = None  # Номер телефона (опционально)
    owner_name: Optional[str] = None  # Владелец счета (опционально)
    bank_name: str  # Название банка
