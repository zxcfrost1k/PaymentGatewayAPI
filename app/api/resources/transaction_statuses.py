# app/api/resources/transaction_statuses.py
from typing import List, Dict


class TransactionStatuses:
    # Возможные статусы платежей
    STATUS_PAID = "paid"  # оплачено
    STATUS_UNDERPAID = "underpaid"  # недоплачено
    STATUS_OVERPAID = "overpaid"  # переплачено
    STATUS_PROCESS = "process"  # ожидает оплаты
    STATUS_EXPIRED = "expired"  # просрочена
    STATUS_CANCEL = "cancel"  # отменена мерчантом
    STATUS_ERROR = "error"  # произошла ошибка
    STATUS_CHARGEBACK = "chargeback"  # возврат средств

    # Все статусы для валидации
    ALL_STATUSES: List[str] = [
        STATUS_PAID,
        STATUS_UNDERPAID,
        STATUS_OVERPAID,
        STATUS_PROCESS,
        STATUS_EXPIRED,
        STATUS_CANCEL,
        STATUS_ERROR,
        STATUS_CHARGEBACK
    ]

    # Типы платежных методов
    PAYMENT_METHODS: List[str] = [
        "card",
        "sbp",
        "qr",
        "sim"
    ]

    # Типы транзакций
    TRANSACTION_TYPES: List[str] = [
        "in",  # входящий платеж
        "out"  # исходящий платеж
    ]


transaction_statuses = TransactionStatuses()