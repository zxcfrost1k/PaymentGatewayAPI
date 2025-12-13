# ВАЛИДНЫЕ ЗНАЧЕНИЯ
from typing import List


# Валидные значения
class ValidRes:
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
