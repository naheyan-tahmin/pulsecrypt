from sqlalchemy import Integer, LargeBinary, ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from ..database import Base


class SessionToken(Base):
    __tablename__ = "session_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    stage: Mapped[str] = mapped_column(String(16))  # pre2fa | active
    blob_enc: Mapped[bytes] = mapped_column(LargeBinary)
    mac_tag: Mapped[bytes] = mapped_column(LargeBinary)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
