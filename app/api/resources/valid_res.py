# ВАЛИДНЫЕ ЗНАЧЕНИЯ
from typing import List


# Валидные значения
class ValidRes:
    valid_bank_names: List[str] = ["Альфа-Банк"] # Внести все названия поддерживаемых банков
    valid_bank_numbers: List[str] = ["1"] # Внести все номера поддерживаемых банков

    valid_currency: List[str] = ["RUB"] # Поддержка только RUB


# Создание объекта класса ValidRes
valid_res = ValidRes
