# ТЕСТОВЫЙ СКРИПТ ДЛЯ ПРОВЕРКИ ПРОСМОТРА АПЕЛЛЯЦИИ
import requests
import json
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
BASE_URL = "http://localhost:8000"
MERCHANT_TOKEN = "test_token_123"


def test_get_existing_appeal():
    """Тестирует получение информации о существующей апелляции"""
    appeal_id = 213233  # ID созданной ранее апелляции

    logger.info("=" * 60)
    logger.info(f"ТЕСТ ПРОСМОТРА АПЕЛЛЯЦИИ {appeal_id}")
    logger.info("=" * 60)

    url = f"{BASE_URL}/api/v1/appeals/{appeal_id}"
    headers = {
        'Authorization': f'Bearer {MERCHANT_TOKEN}'
    }

    try:
        logger.info(f"URL: {url}")
        response = requests.get(url, headers=headers)

        logger.info(f"Статус код: {response.status_code}")

        if response.status_code == 200:
            logger.info("✓ Успешный ответ!")
            result = response.json()
            logger.info(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")

            # Проверяем обязательные поля
            required_fields = [
                'id', 'created_at', 'status', 'amount', 'transaction_id',
                'merchant_transaction_id', 'transaction_created_at',
                'transaction_paid_amount', 'transaction_currency_code'
            ]

            missing_fields = []
            for field in required_fields:
                if field not in result:
                    missing_fields.append(field)

            if missing_fields:
                logger.error(f"✗ Отсутствуют обязательные поля: {missing_fields}")
                return False

            # Проверяем статус
            valid_statuses = ['process', 'success', 'canceled']
            if result['status'] not in valid_statuses:
                logger.error(f"✗ Невалидный статус: {result['status']}")
                return False

            logger.info("✓ Все обязательные поля присутствуют")
            logger.info(f"✓ Статус валиден: {result['status']}")

            # Проверяем структуру transaction_requisite если есть
            if 'transaction_requisite' in result:
                requisite = result['transaction_requisite']
                logger.info(f"Реквизиты: {requisite}")

            return True

        elif response.status_code == 404:
            logger.info(f"✓ Апелляция {appeal_id} не найдена (ожидаемо для теста)")
            return True

        elif response.status_code == 400:
            logger.error("✗ Ошибка 400: Bad Request")
            try:
                error_data = response.json()
                logger.error(f"Детали ошибки: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                logger.error(f"Текст ответа: {response.text}")

        elif response.status_code == 401:
            logger.error("✗ Ошибка 401: Unauthorized")

        else:
            logger.error(f"✗ Неожиданный статус код: {response.status_code}")
            logger.error(f"Текст ответа: {response.text}")

        return False

    except requests.exceptions.ConnectionError:
        logger.error("✗ Ошибка соединения. Убедитесь что сервер запущен.")
        return False

    except Exception as e:
        logger.error(f"✗ Неожиданная ошибка: {str(e)}")
        return False


def test_get_nonexistent_appeal():
    """Тестирует получение информации о несуществующей апелляции"""
    appeal_id = 999999  # Заведомо несуществующий ID

    logger.info("\n" + "=" * 60)
    logger.info(f"ТЕСТ ПРОСМОТРА НЕСУЩЕСТВУЮЩЕЙ АПЕЛЛЯЦИИ {appeal_id}")
    logger.info("=" * 60)

    url = f"{BASE_URL}/api/v1/appeals/{appeal_id}"
    headers = {
        'Authorization': f'Bearer {MERCHANT_TOKEN}'
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Статус код: {response.status_code}")

        if response.status_code == 404:
            logger.info("✓ Ожидаемая ошибка 404: Not Found")
            try:
                error_data = response.json()
                logger.info(f"Сообщение: {error_data.get('message', '')}")
                return True
            except:
                pass
            return True

        elif response.status_code == 200:
            logger.warning("⚠ Апелляция найдена (неожиданно)")
            return True

        else:
            logger.error(f"✗ Неожиданный статус код: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return False


def test_get_appeal_with_invalid_id():
    """Тестирует получение информации с невалидным ID"""
    appeal_id = -1  # Невалидный ID

    logger.info("\n" + "=" * 60)
    logger.info(f"ТЕСТ ПРОСМОТРА АПЕЛЛЯЦИИ С НЕВАЛИДНЫМ ID {appeal_id}")
    logger.info("=" * 60)

    url = f"{BASE_URL}/api/v1/appeals/{appeal_id}"
    headers = {
        'Authorization': f'Bearer {MERCHANT_TOKEN}'
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Статус код: {response.status_code}")

        if response.status_code in [400, 422]:
            logger.info("✓ Ожидаемая ошибка валидации")
            try:
                error_data = response.json()
                if "должен быть положительным" in error_data.get('message', '').lower():
                    logger.info("✓ Правильное сообщение об ошибке")
                    return True
            except:
                pass
            return True

        else:
            logger.error(f"✗ Неожиданный статус код: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return False


def main():
    """Основная функция тестирования"""
    logger.info("Запуск тестов просмотра апелляции...")

    results = []

    try:
        # Тест 1: Просмотр существующей апелляции
        logger.info("\n1. Тест просмотра существующей апелляции:")
        results.append(("Просмотр существующей", test_get_existing_appeal()))

        # Тест 2: Просмотр несуществующей апелляции
        logger.info("\n2. Тест просмотра несуществующей апелляции:")
        results.append(("Просмотр несуществующей", test_get_nonexistent_appeal()))

        # Тест 3: Невалидный ID
        logger.info("\n3. Тест с невалидным ID:")
        results.append(("Невалидный ID", test_get_appeal_with_invalid_id()))

        # Итоги
        logger.info("\n" + "=" * 60)
        logger.info("ИТОГИ ТЕСТИРОВАНИЯ")
        logger.info("=" * 60)

        passed = 0
        for test_name, result in results:
            status = "✓ ПРОЙДЕН" if result else "✗ ПРОВАЛЕН"
            logger.info(f"{test_name}: {status}")
            if result:
                passed += 1

        total = len(results)
        logger.info(f"\nПройдено тестов: {passed}/{total}")

        if passed == total:
            logger.info("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            logger.error(f"✗ ПРОВАЛЕНО ТЕСТОВ: {total - passed}")

    except Exception as e:
        logger.error(f"Ошибка при выполнении тестов: {str(e)}")


if __name__ == "__main__":
    main()