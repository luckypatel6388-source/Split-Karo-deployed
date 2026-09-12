from pydantic import BaseModel, ConfigDict, EmailStr,Field


class UpdateUPIRequest(BaseModel):
    upi_id: str = Field(
        min_length=5,
        max_length=100,
    )


class UpdateUPIResponse(BaseModel):
    user_id: str
    upi_id: str
    upi_verified: bool
    message: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    avatar_url: str | None = None
    is_verified: bool
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
