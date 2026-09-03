from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    national_id: str | None = None
    address: str | None = None
    blood_type: str | None = None
    date_of_birth: str | None = None
    emergency_contact: str | None = None


class ProfileView(BaseModel):
    id: int
    username: str
    email: str
    phone: str
    full_name: str
    national_id: str
    role: str
    address: str
    blood_type: str
    date_of_birth: str
    emergency_contact: str


class PublicUser(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool


class AdminUserList(BaseModel):
    users: list[PublicUser]
