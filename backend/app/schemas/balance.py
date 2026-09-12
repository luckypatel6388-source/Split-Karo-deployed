from decimal import Decimal

from pydantic import BaseModel


class UserBalanceResponse(BaseModel):
    user_id: str
    user_name: str
    balance: Decimal


class GroupBalanceResponse(BaseModel):
    group_id: str
    balances: list[UserBalanceResponse]


class ExpenseHistoryParticipantResponse(BaseModel):
    user_id: str
    user_name: str
    share_amount: Decimal


class ExpenseHistoryItemResponse(BaseModel):
    expense_id: str
    title: str
    amount: Decimal
    paid_by: str
    payer_name: str
    split_type: str
    participants: list[
        ExpenseHistoryParticipantResponse
    ]