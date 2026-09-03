from datetime import datetime
from pydantic import BaseModel


class RecordCreate(BaseModel):
    title: str
    body: str
    diagnosis: str = ""
    owner_id: int | None = None  # doctors may author a note on a patient's chart


class RecordUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    diagnosis: str | None = None


class RecordView(BaseModel):
    id: int
    owner_id: int
    author_id: int
    title: str
    body: str
    diagnosis: str
    created_at: datetime
    updated_at: datetime
    shared: bool = False


class DhStartRequest(BaseModel):
    peer_user_id: int


class DhAcceptRequest(BaseModel):
    exchange_id: int


class DhView(BaseModel):
    id: int
    initiator_id: int
    peer_id: int
    status: str
    params: dict
    initiator_public: str
    peer_public: str | None
    shared_secret_hash_hex: str | None = None


class ShareRequest(BaseModel):
    record_id: int
    exchange_id: int
