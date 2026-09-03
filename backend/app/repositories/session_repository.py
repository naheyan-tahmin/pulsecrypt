from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..models.session_token import SessionToken


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, token: SessionToken) -> SessionToken:
        self.db.add(token)
        self.db.flush()
        return token

    def get_by_hash(self, token_hash: str) -> SessionToken | None:
        return self.db.query(SessionToken).filter(SessionToken.token_hash == token_hash).first()

    def revoke_user(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        rows = self.db.query(SessionToken).filter(
            SessionToken.user_id == user_id,
            SessionToken.revoked == 0,
            SessionToken.expires_at > now,
        )
        for row in rows:
            row.revoked = 1
