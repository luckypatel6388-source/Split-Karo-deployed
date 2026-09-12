from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ExpenseParticipantRequest(BaseModel):
    user_id: str
    share_amount: Decimal | None = Field(
        default=None,
        ge=0,
    )


class CreateExpenseRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    paid_by: str

    split_type: str

    participant_user_ids: list[str] = Field(
        min_length=1,
    )

    custom_shares: list[ExpenseParticipantRequest] | None = None

    @field_validator("split_type")
    @classmethod
    def validate_split_type(cls, value: str) -> str:
        allowed = {
            "equal",
            "custom",
        }

        if value not in allowed:
            raise ValueError(
                "split_type must be 'equal' or 'custom'."
            )

        return value


class ExpenseParticipantResponse(BaseModel):
    user_id: str
    user_name: str
    share_amount: Decimal


class ExpenseResponse(BaseModel):
    id: str
    group_id: str
    title: str
    description: str | None
    amount: Decimal
    paid_by: str
    split_type: str
    participants: list[ExpenseParticipantResponse]