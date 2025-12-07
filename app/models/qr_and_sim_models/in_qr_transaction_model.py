# МОДЕЛИ ДАННЫХ (PayIn | QR НСПК)
from datetime import datetime
from pydantic import BaseModel


class InQrTransactionResponse(BaseModel):
    id: int  # Идентификатор платежа в системе провайдера
    merchant_transaction_id: str  # Идентификатор платежа в системе мерчанта
    expires_at: datetime  # Срок действия платежа
    amount: str  # Сумма транзакции
    currency: str  # Валюта
    currency_rate: str  # Курс валюты
    amount_in_usd: str  # Сумма транзакции в USD
    rate: str  # Тариф
    commission: str  # Коммисия
    payment_url: str  # Ссылка на оплату по QR-коду
