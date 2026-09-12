from pydantic import BaseModel


class RemoveMemberResponse(BaseModel):
    message: str


class LeaveGroupResponse(BaseModel):
    message: str