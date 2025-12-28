# СЕРВИС ПРОВАЙДЕРА GAREX
import httpx
from fastapi import HTTPException

from app.api.services.provider_services.garex_service import tools
from app.core.config import settings
from app.models.paygatecore.pay_in_bank_model import (
    PayInBankResponse,
    PayInBankRequest,
    PayInBankResponse2
)
from app.models.paygatecore.pay_in_model import PayInRequest, PayInResponse, PayInResponse2
from app.api.resources.garex_resources.bank_resources import bank_res
from app.api.resources.garex_resources.transaction_resources import transactions_res
from app.models.paygatecore.pay_out_model import PayOutRequest, PayOutResponse, PayOutRequest2
from app.models.paygatecore.pay_in_sim_model import PayInSimResponse


HEADERS = {
        "Authorization": f"Bearer {settings.providers["garex"]["api_key"]}",
        "Content-Type": "application/json"
    }


def _handle_provider_status(status_code):
    if status_code == 422:
        raise HTTPException(
            status_code=status_code,
            detail={
                "code": "422",
                "message": "Оффер с таким orderId уже существует"
            }
        )

    elif status_code == 404:
        raise HTTPException(
            status_code=status_code,
            detail={
                "code": "404",
                "message": "Объявление, по заданным параметрам, не было найдено"
            }
        )

    elif status_code == 400:
        raise HTTPException(
            status_code=status_code,
            detail={
                "code": "400",
                "message": "Объявление найдено, но отсутствует свободный реквизит"
            }
        )

    elif status_code == 500:
        raise HTTPException(
            status_code=status_code,
            detail={
                "code": "500",
                "message": "Ошибка получения необходимых данных для создания оффера"
            }
        )

    else:
        raise HTTPException(
            status_code=status_code,
            detail={
                "code": f"{status_code}",
                "message": "Непредвиденная ошибка при обращении к провайдеру"
            }
        )


class GarexService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )


    async def pay_in_card(self, request: PayInRequest) -> PayInResponse:
        try:
            method = transactions_res.PAYMENT_METHODS_CARD[0]
            provider_payload = tools.transform_to_provider_format(request, method)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format(provider_response)

        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


    async def pay_in_internal_card(self, request: PayInBankRequest) -> PayInBankResponse:
        try:
            try:
                bank_code = bank_res.BANKS_RUS[request.bank_name]
            except KeyError:
                try:
                    bank_code = bank_res.BANKS_AZN[request.bank_name]
                except KeyError:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "code": "404",
                            "message": f"Банк: {request.bank_name} не найден в системе провайдера"
                        }
                    )

            try:
                method = transactions_res.PAYMENT_METHODS_CARD_ITERNAL[bank_code]
            except KeyError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "400",
                        "message": f"Провайдер не поддерживает такой внутрибанк: {request.bank_name}"}
                )

            provider_payload = tools.transform_to_provider_format_with_bank(request, method, bank_code)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format_with_bank(provider_response)

        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


    async def pay_in_transgran_card(self, request: PayInRequest) -> PayInResponse2:
        try:
            method = transactions_res.PAYMENT_METHODS_CARD_TRANSGRAN[0]
            provider_payload = tools.transform_to_provider_format(request, method)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format_2(provider_response)

        except HTTPException as e:
            if e.status_code == 404 or e.status_code == 400:
                method = transactions_res.PAYMENT_METHODS_CARD_TRANSGRAN[1]
                provider_payload = tools.transform_to_provider_format(request, method)
                response = await self.client.post(
                    f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                    headers=HEADERS,
                    json=provider_payload
                )
                _handle_provider_status(response.status_code)
                response.raise_for_status()
                provider_response = response.json()

                return tools.transform_from_provider_format_2(provider_response)

            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


    async def pay_in_sbp(self, request: PayInRequest) -> PayInBankResponse:
        try:
            method = transactions_res.PAYMENT_METHODS_SBP[0]
            provider_payload = tools.transform_to_provider_format(request, method)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format_with_bank(provider_response)

        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


    async def pay_in_internal_sbp(self, request: PayInBankRequest) -> PayInBankResponse2:
        try:
            try:
                bank_code = bank_res.BANKS_RUS[request.bank_name]
            except KeyError:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "404",
                        "message": f"Банк: {request.bank_name} не найден в системе провайдера"                        }
                )

            method = transactions_res.PAYMENT_METHODS_SBP[0]
            provider_payload = tools.transform_to_provider_format_with_bank(request, method, bank_code)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format_with_bank_2(provider_response)

        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


    async def pay_in_transgran_sbp(self, request: PayInRequest) -> PayInBankResponse2:
        try:
            method = transactions_res.PAYMENT_METHODS_SBP_TRANSGRAN[0]
            provider_payload = tools.transform_to_provider_format(request, method)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format_with_bank_2(provider_response)

        except HTTPException as e:
            if e.status_code == 404 or e.status_code == 400:
                method = transactions_res.PAYMENT_METHODS_SBP_TRANSGRAN[1]
                provider_payload = tools.transform_to_provider_format(request, method)
                response = await self.client.post(
                    f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                    headers=HEADERS,
                    json=provider_payload
                )
                _handle_provider_status(response.status_code)
                response.raise_for_status()
                provider_response = response.json()

                return tools.transform_from_provider_format_with_bank_2(provider_response)

            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


    async def pay_in_qr(self):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "400",
                "message": "Провайдер не поддерживает данный вид оплаты: qr"
            }
        )


    async def pay_in_sim(self, request: PayInRequest) -> PayInSimResponse:
        try:
            method = transactions_res.PAYMENT_METHODS_SIM[0]
            provider_payload = tools.transform_to_provider_format(request, method)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payin",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format_3(provider_response)

        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


    async def pay_out_card(self, request: PayOutRequest) -> PayOutResponse:
        try:
            method = transactions_res.PAYMENT_METHODS_CARD[0]
            provider_payload = tools.transform_to_provider_format_for_out(request, method)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payout",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format_for_out(provider_response)

        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


    async def pay_out_sbp(self, request: PayOutRequest2) -> PayOutResponse:
        try:
            try:
                # Наши коды?
                bank_code = "sber" # Заглушка
            except KeyError:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "404",
                        "message": f"Банк: {request.bank_name} не найден в системе провайдера"                        }
                )

            method = transactions_res.PAYMENT_METHODS_SBP[0]
            provider_payload = tools.transform_to_provider_format_for_out_2(request, method, bank_code)
            response = await self.client.post(
                f"{settings.providers["garex"]["base_url"]}/api/merchant/payments/payout",
                headers=HEADERS,
                json=provider_payload
            )
            _handle_provider_status(response.status_code)
            response.raise_for_status()
            provider_response = response.json()

            return tools.transform_from_provider_format_for_out(provider_response)

        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )


garex = GarexService()
