from sqlalchemy import Integer, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from ..database import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    address_enc: Mapped[bytes] = mapped_column(LargeBinary, default=b"")
    blood_type_enc: Mapped[bytes] = mapped_column(LargeBinary, default=b"")
    date_of_birth_enc: Mapped[bytes] = mapped_column(LargeBinary, default=b"")
    emergency_contact_enc: Mapped[bytes] = mapped_column(LargeBinary, default=b"")
    mac_tag: Mapped[bytes] = mapped_column(LargeBinary)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="profile")
