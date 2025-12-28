# MIDDLEWARE ДЛЯ АУТЕНТИФИКАЦИИ
from typing import Dict, Any, Optional, List
import logging

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings


logger = logging.getLogger(__name__)


# Проверка токена
def verify_token(token: str) -> bool:
    logger.info(f"Verifying token. Expected: {settings.merchant_token}, Received: {token}")
    return token == settings.merchant_token


# Создание ответа об ошибке
def _create_error_response(code: str,
                           message: str,
                           errors: Optional[Dict[str,
                           List[str]]] = None) -> Dict[str, Any]:
    error_response: Dict[str, Any] = {
        "code": code,
        "message": message
    }

    # Поле errors только при множественных ошибках
    if errors and len(errors) > 1:
        error_response["errors"] = errors

    return error_response


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            logger.info(f"Received credentials: {credentials}")

            # Проверка на отсутствие учетных данных
            if not credentials:
                logger.warning("No credentials provided")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=_create_error_response(
                        code="401",
                        message="Отсутствует схема авторизации"
                    )
                )

            # Проверка схемы аутентификации
            if not credentials.scheme == "Bearer":
                logger.warning(f"Invalid scheme: {credentials.scheme}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=_create_error_response(
                        code="401",
                        message="Неверная схема аутентификации"
                    )
                )

            # Проверка валидности токена
            if not verify_token(credentials.credentials):
                logger.warning("Token verification failed")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=_create_error_response(
                        code="401",
                        message="Недействительный токен"
                    )
                )

            logger.info("Token verification successful")
            return credentials.credentials

        # Проброс уже созданных HTTPException
        except HTTPException as e:
            logger.error(f"HTTPException in auth: {e.detail}")
            raise e

        except Exception as e:
            logger.error(f"Unexpected error in auth: {str(e)}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=_create_error_response(
                    code="401",
                    message="Ошибка службы аутентификации"
                )
            )


# Создание объекта класса JWTBearer
security = JWTBearer()
