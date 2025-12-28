# СЕРВИС ПРОВЕРКИ ПОДПИСИ
import hashlib
import hmac
import json
from urllib.parse import urlparse
from typing import Dict, Any
import logging


logger = logging.getLogger(__name__)


# Вычисление подписи для вебхука
def calculate_signature(url: str, request_body: Dict[str, Any], secret: str) -> str:
    try:
        request_json_string = json.dumps(request_body)
        parsed_url = urlparse(url)
        signature_string = request_json_string + parsed_url.path + parsed_url.query

        # HMAC SHA-256
        signature = hmac.new(
            secret.encode("utf-8"),
            signature_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().lower()

        return signature

    except Exception as e:
        logger.error(f"Error with calculate signature: {str(e)}")
        raise


# Проверка подписи вебхука
def verify_signature(url: str, request_body: Dict[str, Any], signature_header: str, secret: str) -> bool:
    if not signature_header:
        logger.warning("No headers: X-Signature")
        return False

    try:
        expected_signature = calculate_signature(url, request_body, secret)
        return hmac.compare_digest(expected_signature, signature_header.lower())

    except Exception as e:
        logger.error(f"Error with verify signature: {str(e)}")
        return False
