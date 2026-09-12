from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel


class ExpenseParticipantDetail(BaseModel):
    user_id: str
    user_name: str
    share_amount: Decimal


class ExpenseItemParticipantDetail(BaseModel):
    user_id: str
    user_name: str
    share_amount: Decimal


class ExpenseItemDetail(BaseModel):
    id: str
    name: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    participants: list[
        ExpenseItemParticipantDetail
    ]


class ExpenseUpdateLogResponse(BaseModel):
    id: str
    updated_by: str
    updated_by_name: str
    previous_amount: Decimal | None
    updated_amount: Decimal | None
    previous_title: str | None
    updated_title: str | None
    previous_description: str | None
    updated_description: str | None
    changed_at: datetime


class ExpenseDetailResponse(BaseModel):
    id: str
    group_id: str
    title: str
    description: str | None
    amount: Decimal
    paid_by: str
    payer_name: str
    split_type: str

    participants: list[
        ExpenseParticipantDetail
    ]

    items: list[
        ExpenseItemDetail
    ]

    update_logs: list[ExpenseUpdateLogResponse]

