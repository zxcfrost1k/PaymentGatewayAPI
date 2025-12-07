# МОДЕЛИ ДАННЫХ (PayIn | СИМ-карта)
from datetime import datetime
from pydantic import BaseModel


class InSimTransactionResponse(BaseModel):
    id: int  # Идентификатор платежа в системе провайдера
    merchant_transaction_id: str  # Идентификатор платежа в системе мерчанта
    expires_at: datetime  # Срок действия платежа
    amount: str  # Сумма транзакции
    currency: str  # Валюта
    currency_rate: str  # Курс валюты
    amount_in_usd: str  # Сумма транзакции в USD
    rate: str  # Тариф
    commission: str  # Коммисия
    phone_number: str # Номер телефона
    owner_name: str # Владелец карты
    operator: str # Название мобильного оператора
