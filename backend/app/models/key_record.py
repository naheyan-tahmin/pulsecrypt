from sqlalchemy import Integer, LargeBinary, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from ..database import Base


class KeyRecord(Base):
    __tablename__ = "key_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    key_type: Mapped[str] = mapped_column(String(16))  # rsa | ecc | dh
    version: Mapped[int] = mapped_column(Integer, default=1)
    public_key: Mapped[bytes] = mapped_column(LargeBinary)
    private_key_enc: Mapped[bytes] = mapped_column(LargeBinary)
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    mac_tag: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="keys")


class DhExchange(Base):
    __tablename__ = "dh_exchanges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    initiator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    peer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    params_json: Mapped[str] = mapped_column(Text)
    initiator_public: Mapped[str] = mapped_column(Text)
    peer_public: Mapped[str | None] = mapped_column(Text, nullable=True)
    initiator_private_enc: Mapped[bytes] = mapped_column(LargeBinary)
    peer_private_enc: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    shared_secret_hash: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    mac_tag: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
