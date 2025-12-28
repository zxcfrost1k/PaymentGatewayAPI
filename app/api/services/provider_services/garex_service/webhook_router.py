# РОУТЕР ВЕБХУКОВ ПРОВАЙДЕРА GAREX
import httpx
from fastapi import APIRouter, HTTPException
import logging
from typing import Dict, Any
import asyncio

from app.core.config import settings
from app.models.garex.webhook_model import WebhookRequest as WebhookRequestFrom
from app.models.paygatecore.other_models import WebhookRequest as WebhookRequestTo
from app.api.resources.garex_resources.transaction_resources import transactions_res


logger = logging.getLogger(__name__)
router = APIRouter()


async def _send_callback(webhook_url:str, webhook_data: WebhookRequestTo):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook_url,
                json=webhook_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info(f"Webhook sent successfully to: {webhook_url}")

    except Exception as e:
        logger.info(f"Webhook sent failed: {str(e)}")


def _check_paid_amount(state: str) -> bool:
    if state in [
        transactions_res.STATUS_PAID,
        transactions_res.STATUS_FINISHED
                 ]:
        return True
    return False


@router.post("/garex", status_code=200)
async def handle_transaction_webhook(
        webhook_data_from: Dict[str, Any]
):
    try:
        webhook = WebhookRequestFrom(**webhook_data_from)
        logger.info(f"New webhook: {webhook.orderId}")

        if webhook.state not in transactions_res.ALL_STATUSES:
            logger.info(f"Unknown transaction: {webhook.orderId} status: {webhook.state}")
            raise

        if webhook.state == transactions_res.STATUS_CREATED:
            logger.info(f"Transaction created: {webhook.orderId}")
            raise

        elif webhook.state == transactions_res.STATUS_PENDING:
            logger.info(f"Transaction pending payment: {webhook.orderId}")
            raise

        elif webhook.state == transactions_res.STATUS_PAID:
            logger.info(f"Transaction paid: {webhook.orderId}")

        elif webhook.status == transactions_res.STATUS_FINISHED:
            logger.info(f"Transaction finished successfully: {webhook.orderId}")
            raise

        elif webhook.status == transactions_res.STATUS_CANCELED:
            logger.info(f"Transaction cancelled: {webhook.orderId}")

        elif webhook.status == transactions_res.STATUS_DISPUTE:
            logger.info(f"Transaction disputing: {webhook.orderId}")
            raise

        elif webhook.status == transactions_res.STATUS_FAILED:
            logger.info(f"Transaction failed: {webhook.orderId}")

        webhook_data_to = WebhookRequestTo(
            id=webhook.id,
            merchant_transaction_id=webhook.orderId,
            type="",
            amount=str(webhook.amount),
            paid_amount=str(webhook.amount) if _check_paid_amount(webhook.state) else "0",
            currency="RUB",
            currency_rate=str(webhook.rate),
            amount_in_usd=str(webhook.amount / webhook.rate),
            status=webhook.state
        )

        webhook_url = settings.webhook_base_url
        asyncio.create_task(
            _send_callback(webhook_url, webhook_data_to)
        )

        return {
            "code": "200",
            "message": "Webhook processed successfully"
        }

    except Exception as e:
        logger.error(f"Error with webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке вебхука: {str(e)}"
        )
