from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseItemParticipantRequest(BaseModel):
    user_id: str

    share_amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )


class CreateExpenseItemRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    quantity: Decimal = Field(
        default=Decimal("1.00"),
        gt=0,
        max_digits=10,
        decimal_places=2,
    )

    unit_price: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    participants: list[
        ExpenseItemParticipantRequest
    ] = Field(
        min_length=1,
    )


class ExpenseItemParticipantResponse(BaseModel):
    user_id: str
    user_name: str
    share_amount: Decimal


class ExpenseItemResponse(BaseModel):
    id: str
    name: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal

    participants: list[
        ExpenseItemParticipantResponse
    ]