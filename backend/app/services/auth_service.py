from __future__ import annotations

from sqlalchemy.orm import Session

from ..config import settings
from ..crypto_core.hashing.custom_hash import sha256
from ..crypto_core.hashing.password_hash import hash_password_for_storage, verify_password
from ..crypto_core.totp.totp import generate_secret, verify_totp, provisioning_uri, secret_to_base32
from ..models.user import User
from ..models.patient_profile import PatientProfile
from ..repositories.user_repository import UserRepository
from ..services.encryption_service import EncryptionService
from ..services.key_service import KeyService
from ..services.session_service import SessionService
from ..core.exceptions import AuthError, ForbiddenError
from ..schemas.auth_schemas import RegisterRequest, TokenResponse


def username_hash(username: str) -> str:
    return sha256(username.strip().lower().encode("utf-8")).hex()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.keys = KeyService(db)
        self.enc = EncryptionService(db)
        self.sessions = SessionService(db)

    def register(self, req: RegisterRequest) -> TokenResponse:
        uh = username_hash(req.username)
        if self.users.get_by_username_hash(uh):
            raise AuthError("username already exists", 409)
        # Additional check: prevent registration with different case versions of existing usernames
        for existing_user in self.users.list_all():
            try:
                existing_username = self.enc.dec_pii(existing_user.id, existing_user.username_enc)
                if existing_username.lower() == req.username.strip().lower() and existing_username != req.username.strip():
                    raise AuthError("username already exists (case variant)", 409)
            except Exception:
                continue
        stored = hash_password_for_storage(req.password, settings.password_iterations)
        user = User(
            username_hash=uh,
            username_enc=b"\x00",
            email_enc=b"\x00",
            phone_enc=b"\x00",
            full_name_enc=b"\x00",
            national_id_enc=b"\x00",
            role_enc=b"\x00",
            password_stored=stored,
            totp_secret_enc=b"\x00",
            totp_confirmed=True,
            pii_mac=b"\x00",
            is_active=True,
        )
        self.users.add(user)
        self.db.flush()
        self.keys.issue_user_keys(user.id)

        totp_secret = generate_secret()
        user.username_enc = self.enc.enc_pii(user.id, req.username.strip())
        user.email_enc = self.enc.enc_pii(user.id, req.email)
        user.phone_enc = self.enc.enc_pii(user.id, req.phone)
        user.full_name_enc = self.enc.enc_pii(user.id, req.full_name)
        user.national_id_enc = self.enc.enc_pii(user.id, req.national_id)
        user.role_enc = self.enc.enc_pii(user.id, req.role)
        user.totp_secret_enc = self.enc.enc_pii(user.id, totp_secret.hex())
        user.pii_mac = self.enc.pii_mac(
            user.username_enc, user.email_enc, user.phone_enc,
            user.full_name_enc, user.national_id_enc, user.role_enc,
        )
        profile = PatientProfile(
            user_id=user.id,
            address_enc=self.enc.enc_pii(user.id, ""),
            blood_type_enc=self.enc.enc_pii(user.id, ""),
            date_of_birth_enc=self.enc.enc_pii(user.id, ""),
            emergency_contact_enc=self.enc.enc_pii(user.id, ""),
            mac_tag=b"",
        )
        profile.mac_tag = self.enc.pii_mac(
            profile.address_enc, profile.blood_type_enc,
            profile.date_of_birth_enc, profile.emergency_contact_enc,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(user)
        token = self.sessions.issue(user.id, "pre2fa")
        return TokenResponse(
            access_token=token,
            stage="pre2fa",
            totp_uri=provisioning_uri(totp_secret, req.username),
            totp_secret=secret_to_base32(totp_secret),
        )

    def login(self, username: str, password: str) -> TokenResponse:
        user = self.users.get_by_username_hash(username_hash(username))
        if not user or not user.is_active:
            raise AuthError("invalid credentials")
        if not verify_password(password, user.password_stored):
            raise AuthError("invalid credentials")
        # Verify exact username match (case-sensitive) for security
        try:
            stored_username = self.enc.dec_pii(user.id, user.username_enc)
            if stored_username != username.strip():
                raise AuthError("invalid credentials")
        except Exception:
            raise AuthError("invalid credentials")
        token = self.sessions.issue(user.id, "pre2fa")
        return TokenResponse(access_token=token, stage="pre2fa")

    def verify_2fa(self, pre2fa_token: str, code: str) -> TokenResponse:
        payload = self.sessions.parse(pre2fa_token)
        if payload["stage"] != "pre2fa":
            raise AuthError("expected a pre-2FA token")
        user = self.users.get_by_id(payload["sub"])
        if not user:
            raise AuthError("user missing")
        secret_hex = self.enc.dec_pii(user.id, user.totp_secret_enc)
        secret = bytes.fromhex(secret_hex)
        if not verify_totp(secret, code):
            raise AuthError("invalid authenticator code")
        rec = self.sessions.repo.get_by_hash(sha256(bytes.fromhex(payload["sid"])).hex())
        if rec:
            rec.revoked = 1
        token = self.sessions.issue(user.id, "active")
        return TokenResponse(access_token=token, stage="active")

    def decrypt_role(self, user: User) -> str:
        return self.enc.dec_pii(user.id, user.role_enc)

    def seed_admin(self) -> None:
        if self.users.get_by_username_hash(username_hash(settings.admin_username)):
            return
        req = RegisterRequest(
            username=settings.admin_username,
            password=settings.admin_password,
            email=settings.admin_email,
            phone="",
            full_name="PulseCrypt Administrator",
            national_id="",
            role="patient",
        )
        enrolled = self.register(req)
        user = self.users.get_by_username_hash(username_hash(settings.admin_username))
        if user:
            user.role_enc = self.enc.enc_pii(user.id, "admin")
            user.pii_mac = self.enc.pii_mac(
                user.username_enc, user.email_enc, user.phone_enc,
                user.full_name_enc, user.national_id_enc, user.role_enc,
            )
            self.db.commit()
        from pathlib import Path
        note = Path(settings.master_key_path).parent / "admin_totp.txt"
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            f"username={settings.admin_username}\n"
            f"password={settings.admin_password}\n"
            f"totp_secret={enrolled.totp_secret}\n"
            f"totp_uri={enrolled.totp_uri}\n",
            encoding="utf-8",
        )
