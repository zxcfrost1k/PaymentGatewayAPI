# ВАЛИДНЫЕ ЗНАЧЕНИЯ
from typing import List


# Валидные значения
class ValidRes:
    valid_bank_names: List[str] = ["Альфа-Банк"] # Внести все названия поддерживаемых банков
    valid_bank_numbers: List[str] = ["1"] # Внести все номера поддерживаемых банков

    valid_currency: List[str] = ["RUB"] # Поддержка только RUB

    # Статусы апелляции
    valid_appeal_statuses: List[str] = [
        "process",  # в обработке
        "success",  # одобрена
        "canceled"  # отклонена
    ]

    # Поддерживаемые типы файлов для вложений
    valid_file_types: List[str] = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "video/mp4",
        "video/mpeg",
        "application/pdf"
    ]
    # Поддерживаемые расширения файлов для вложений
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mpeg', '.pdf']

# Создание объекта класса ValidRes
valid_res = ValidRes
