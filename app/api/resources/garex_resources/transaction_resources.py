# ПЛАТЕЖНЫЕ РЕСУРСЫ ПРОВАЙДЕРА GAREX
from typing import List, Dict


class TransactionResources:
    # Возможные статусы платежей
    STATUS_CREATED = "created"  # создан, реквизиты не выданы
    STATUS_PENDING = "pending" # реквизиты выданы, ожидает оплаты
    STATUS_PAID = "paid" # оплачен покупателем
    STATUS_FINISHED = "finished" # успешно завершен
    STATUS_CANCELED = "canceled" # отменен
    STATUS_DISPUTE = "dispute" # в споре
    STATUS_FAILED = "failed" # ошибка создания

    # Все статусы для валидации
    ALL_STATUSES: List[str] = [
        STATUS_CREATED,
        STATUS_PENDING,
        STATUS_PAID,
        STATUS_FINISHED,
        STATUS_CANCELED,
        STATUS_DISPUTE,
        STATUS_FAILED
    ]

    # Типы поддерживаемых платежных методов
    PAYMENT_METHODS_CARD: List[str] = [
        "c2c"
    ]
    PAYMENT_METHODS_CARD_ITERNAL: Dict[str, str] = {
        "sber": "sber2sber",
        "alfa-bank": "alfa2alfa",
        "vtb": "vtb2vtb",
        "t-bank": "tbank2tbank",
        "ozonbank": "ozon2ozon",
    }
    PAYMENT_METHODS_CARD_TRANSGRAN: List[str] = [
        "m2tjs_c2c",
        "m2abh_c2c"
    ]
    PAYMENT_METHODS_SBP: List[str] = [
        "sbp"
    ]
    PAYMENT_METHODS_SBP_TRANSGRAN: List[str] = [
        "m2tjs_sbp",
        "m2abh_sbp"
    ]
    PAYMENT_METHODS_SIM: List[str] = [
        "sim"
    ]
    PAYMENT_METHODS_OTHER: List[str] = [
        "link2pay",
        "bank-account"
        "c2c_wt",
        "sbp_wt"
    ]

    # Типы транзакций
    TRANSACTION_TYPES: List[str] = [
        "in",
        "out"
    ]


transactions_res = TransactionResources
