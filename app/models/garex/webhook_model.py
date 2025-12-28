from pydantic import BaseModel


class WebhookRequest(BaseModel):
    id: int
    state: str
    amount: int
    rate: int
    address: str
    bik: str
    recipient: str
    bank: str
    bankName: str
    sign: str
    orderId: str
    fee: int
