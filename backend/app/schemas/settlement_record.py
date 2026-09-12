from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateSettlementRequest(BaseModel):
    from_user_id: str
    to_user_id: str

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    payment_method: str | None = Field(
        default=None,
        max_length=50,
    )


class MarkSettlementPaidRequest(BaseModel):
    payment_reference: str | None = Field(
        default=None,
        max_length=150,
    )


class SettlementRecordResponse(BaseModel):
    id: str
    group_id: str

    from_user_id: str
    from_user_name: str

    to_user_id: str
    to_user_name: str

    amount: Decimal

    status: str

    payment_method: str | None
    payment_reference: str | None
    paid_at: datetime | None