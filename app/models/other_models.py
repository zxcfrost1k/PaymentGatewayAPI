# ОСТАЛЬНЫЕ МОДЕЛИ ДАННЫХ
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


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


class WebhookRequest(BaseModel):
    id: int # Идентификатор платежа в системе провайдера
    merchant_transaction_id: str # Идентификатор платежа в системе мерчанта
    type: str  # "in" или "out"
    amount: str # # Сумма транзакции
    paid_amount: str # Сумма, на которую была выполнена оплата
    currency: str # Валюта
    currency_rate: str # Курс валюты
    amount_in_usd: str # Сумма транзакции в USD
    status: str # Статус платежа


class BalanceResponse(BaseModel):
    balance: str
    currency_rate: str


class LimitItem(BaseModel):
    min_amount: str = Field(..., description="Минимальная сумма")
    max_amount: str = Field(..., description="Максимальная сумма")


class LimitsResponse(BaseModel):
    card: Optional[LimitItem] = Field(..., description="Лимиты для карточных операций")
    sbp: Optional[LimitItem] = Field(None, description="Лимиты для СБП операций")
    qr: Optional[LimitItem] = Field(None, description="Лимиты для QR операций")
    sim: Optional[LimitItem] = Field(None, description="Лимиты для SIM операций")
