# МОДЕЛИ ДАННЫХ (PayIn | СБП (внутрибанк))
from datetime import datetime
from pydantic import BaseModel


class InInternalSbpTransactionResponse(BaseModel):
    id: int  # Идентификатор платежа (их)
    merchant_transaction_id: str  # Идентификатор платежа (наш)
    expires_at: datetime  # Срок действия платежа
    amount: str  # Сумма транзакции
    currency: str  # Валюта
    currency_rate: str  # Курс валюты
    amount_in_usd: str  # Сумма транзакции в USD
    rate: str  # Тариф
    commission: str  # Коммисия
    phone_number: str  # Номер счета
    owner_name: str  # Владелец счета
    bank_name: str  # Название банка
    country_name: str  # Название страны банка
    payment_currency: str  # Код валюты оплаты
