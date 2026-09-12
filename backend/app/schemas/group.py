from pydantic import BaseModel, Field


class CreateGroupRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class GroupMemberResponse(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    role: str
    is_active: bool


class GroupResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_by: str
    members: list[GroupMemberResponse]


class CreateInviteResponse(BaseModel):
    token: str
    invite_url: str


class InvitePreviewResponse(BaseModel):
    group_id: str
    group_name: str
    group_description: str | None
    expires_at: str | None


class JoinGroupResponse(BaseModel):
    message: str
    group_id: str
    group_name: str