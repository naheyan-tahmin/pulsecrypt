from sqlalchemy import String, Integer, LargeBinary, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    username_enc: Mapped[bytes] = mapped_column(LargeBinary)
    email_enc: Mapped[bytes] = mapped_column(LargeBinary)
    phone_enc: Mapped[bytes] = mapped_column(LargeBinary)
    full_name_enc: Mapped[bytes] = mapped_column(LargeBinary)
    national_id_enc: Mapped[bytes] = mapped_column(LargeBinary)
    role_enc: Mapped[bytes] = mapped_column(LargeBinary)
    password_stored: Mapped[str] = mapped_column(Text)
    totp_secret_enc: Mapped[bytes] = mapped_column(LargeBinary)
    totp_confirmed: Mapped[bool] = mapped_column(Boolean, default=True)
    pii_mac: Mapped[bytes] = mapped_column(LargeBinary)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    profile = relationship("PatientProfile", back_populates="user", uselist=False)
    keys = relationship("KeyRecord", back_populates="user")
    records = relationship("MedicalRecord", back_populates="owner", foreign_keys="MedicalRecord.owner_id")
