from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentInitiateRequest(BaseModel):
    settlement_id: str = Field(
        min_length=36,
        max_length=36,
    )

    idempotency_key: str = Field(
        min_length=16,
        max_length=128,
    )


class PaymentInitiateResponse(BaseModel):
    payment_id: str

    settlement_id: str

    payer_user_id: str
    receiver_user_id: str

    amount: Decimal

    currency: str

    status: str

    payment_method: str

    receiver_upi_id: str | None = None

    upi_uri: str | None = None

    message: str

    idempotent_replay: bool = False


"""from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentInitiateRequest(BaseModel):
    settlement_id: str = Field(
        min_length=36,
        max_length=36,
    )

    idempotency_key: str = Field(
        min_length=16,
        max_length=128,
    )


class PaymentInitiateResponse(BaseModel):
    payment_id: str

    settlement_id: str

    payer_user_id: str
    receiver_user_id: str

    amount: Decimal

    currency: str

    status: str

    payment_method: str

    upi_uri: str | None = None

    message: str

    idempotent_replay: bool = False"""