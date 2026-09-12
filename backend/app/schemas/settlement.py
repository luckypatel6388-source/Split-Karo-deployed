from decimal import Decimal

from pydantic import BaseModel


class SettlementResponse(BaseModel):
    from_user_id: str
    from_user_name: str
    to_user_id: str
    to_user_name: str
    amount: Decimal


class SettlementListResponse(BaseModel):
    group_id: str
    settlements: list[SettlementResponse]