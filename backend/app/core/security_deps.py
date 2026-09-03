from __future__ import annotations
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..services.session_service import SessionService
from ..services.encryption_service import EncryptionService
from ..core.exceptions import AuthError, ForbiddenError


def _bearer(authorization: str | None) -> str:
    if not authorization:
        raise AuthError("missing Authorization header")
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("expected Bearer token")
    return parts[1].strip()


def get_session_payload(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    token = _bearer(authorization)
    return SessionService(db).parse(token)


def get_current_user(
    payload: dict = Depends(get_session_payload),
    db: Session = Depends(get_db),
) -> User:
    if payload.get("stage") != "active":
        raise AuthError("complete two-factor authentication first", 403)
    user = UserRepository(db).get_by_id(payload["sub"])
    if not user or not user.is_active:
        raise AuthError("account disabled or missing")
    return user


def get_current_role(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    return EncryptionService(db).dec_pii(user.id, user.role_enc)


def require_role(*roles: str):
    def _dep(role: str = Depends(get_current_role)) -> str:
        if role not in roles:
            raise ForbiddenError(f"requires role: {', '.join(roles)}")
        return role

    return _dep
