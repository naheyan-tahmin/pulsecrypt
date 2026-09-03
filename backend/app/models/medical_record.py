from sqlalchemy import Integer, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from ..database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    payload_enc: Mapped[bytes] = mapped_column(LargeBinary)
    mac_tag: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    owner = relationship("User", foreign_keys=[owner_id], back_populates="records")


class RecordShare(Base):
    __tablename__ = "record_shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("medical_records.id"), index=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    dh_exchange_id: Mapped[int] = mapped_column(ForeignKey("dh_exchanges.id"))
    payload_enc: Mapped[bytes] = mapped_column(LargeBinary)
    mac_tag: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
