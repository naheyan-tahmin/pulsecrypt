from __future__ import annotations
import json
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..config import settings
from ..crypto_core.rsa.encryption import encrypt as rsa_encrypt, decrypt as rsa_decrypt
from ..crypto_core.hashing.custom_hash import sha256
from ..models.session_token import SessionToken
from ..repositories.session_repository import SessionRepository
from ..services.key_service import get_master
from ..services.mac_service import MacService
from ..utils.encoding import b64e, b64d
from ..core.exceptions import AuthError


class SessionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SessionRepository(db)
        self.master = get_master()
        self.mac = MacService(self.master.mac_key)

    def issue(self, user_id: int, stage: str) -> str:
        ttl = settings.pre2fa_lifetime_seconds if stage == "pre2fa" else settings.session_lifetime_seconds
        expires = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        sid = secrets.token_bytes(16)
        payload = json.dumps(
            {
                "sub": user_id,
                "sid": sid.hex(),
                "stage": stage,
                "exp": int(expires.timestamp()),
            }
        ).encode("utf-8")
        blob = rsa_encrypt(payload, self.master.pair.public)
        tag = self.mac.tag(blob)
        token_hash = sha256(sid).hex()
        rec = SessionToken(
            user_id=user_id,
            token_hash=token_hash,
            stage=stage,
            blob_enc=blob,
            mac_tag=tag,
            expires_at=expires,
            revoked=0,
        )
        self.repo.add(rec)
        self.db.commit()
        return b64e(blob + tag)

    def parse(self, token: str) -> dict:
        try:
            raw = b64d(token)
        except Exception as exc:
            raise AuthError("malformed session token") from exc
        if len(raw) < 33:
            raise AuthError("malformed session token")
        blob, tag = raw[:-32], raw[-32:]
        self.mac.verify(tag, blob)
        try:
            payload = json.loads(rsa_decrypt(blob, self.master.pair.private).decode("utf-8"))
        except Exception as exc:
            raise AuthError("session token decrypt failed") from exc
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if exp < datetime.now(timezone.utc):
            raise AuthError("session expired")
        rec = self.repo.get_by_hash(sha256(bytes.fromhex(payload["sid"])).hex())
        if rec is None or rec.revoked:
            raise AuthError("session revoked or unknown")
        if rec.stage != payload["stage"]:
            raise AuthError("session stage mismatch")
        return payload

    def revoke_user(self, user_id: int) -> None:
        self.repo.revoke_user(user_id)
        self.db.commit()
