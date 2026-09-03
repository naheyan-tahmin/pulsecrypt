from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    email: str
    phone: str = ""
    full_name: str
    national_id: str = ""
    role: str = "patient"

    @field_validator("role")
    @classmethod
    def role_ok(cls, v: str) -> str:
        v = v.lower()
        if v not in {"patient", "doctor"}:
            raise ValueError("role must be patient or doctor")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TotpVerifyRequest(BaseModel):
    pre2fa_token: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    stage: str
    totp_uri: str | None = None
    totp_secret: str | None = None


class MessageResponse(BaseModel):
    message: str
