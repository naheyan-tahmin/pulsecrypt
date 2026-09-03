from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..repositories.record_repository import RecordRepository
from ..services.encryption_service import EncryptionService
from ..schemas.user_schemas import ProfileView, ProfileUpdate, PublicUser
from ..core.exceptions import NotFoundError, IntegrityError


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.records = RecordRepository(db)
        self.enc = EncryptionService(db)

    def _verify_user_mac(self, user: User) -> None:
        expected = self.enc.pii_mac(
            user.username_enc, user.email_enc, user.phone_enc,
            user.full_name_enc, user.national_id_enc, user.role_enc,
        )
        if expected != user.pii_mac:
            raise IntegrityError("user record MAC mismatch")

    def view_profile(self, user: User) -> ProfileView:
        self._verify_user_mac(user)
        profile = self.records.get_profile(user.id)
        address = blood = dob = emergency = ""
        if profile:
            self.enc.mac.verify(
                profile.mac_tag,
                profile.address_enc,
                profile.blood_type_enc,
                profile.date_of_birth_enc,
                profile.emergency_contact_enc,
            )
            address = self.enc.dec_pii(user.id, profile.address_enc)
            blood = self.enc.dec_pii(user.id, profile.blood_type_enc)
            dob = self.enc.dec_pii(user.id, profile.date_of_birth_enc)
            emergency = self.enc.dec_pii(user.id, profile.emergency_contact_enc)
        return ProfileView(
            id=user.id,
            username=self.enc.dec_pii(user.id, user.username_enc),
            email=self.enc.dec_pii(user.id, user.email_enc),
            phone=self.enc.dec_pii(user.id, user.phone_enc),
            full_name=self.enc.dec_pii(user.id, user.full_name_enc),
            national_id=self.enc.dec_pii(user.id, user.national_id_enc),
            role=self.enc.dec_pii(user.id, user.role_enc),
            address=address,
            blood_type=blood,
            date_of_birth=dob,
            emergency_contact=emergency,
        )

    def update_profile(self, user: User, data: ProfileUpdate) -> ProfileView:
        self._verify_user_mac(user)
        if data.email is not None:
            user.email_enc = self.enc.enc_pii(user.id, data.email)
        if data.phone is not None:
            user.phone_enc = self.enc.enc_pii(user.id, data.phone)
        if data.full_name is not None:
            user.full_name_enc = self.enc.enc_pii(user.id, data.full_name)
        if data.national_id is not None:
            user.national_id_enc = self.enc.enc_pii(user.id, data.national_id)
        user.pii_mac = self.enc.pii_mac(
            user.username_enc, user.email_enc, user.phone_enc,
            user.full_name_enc, user.national_id_enc, user.role_enc,
        )
        profile = self.records.get_profile(user.id)
        if profile:
            if data.address is not None:
                profile.address_enc = self.enc.enc_pii(user.id, data.address)
            if data.blood_type is not None:
                profile.blood_type_enc = self.enc.enc_pii(user.id, data.blood_type)
            if data.date_of_birth is not None:
                profile.date_of_birth_enc = self.enc.enc_pii(user.id, data.date_of_birth)
            if data.emergency_contact is not None:
                profile.emergency_contact_enc = self.enc.enc_pii(user.id, data.emergency_contact)
            profile.mac_tag = self.enc.pii_mac(
                profile.address_enc, profile.blood_type_enc,
                profile.date_of_birth_enc, profile.emergency_contact_enc,
            )
        self.db.commit()
        return self.view_profile(user)

    def list_public(self, actor: User, actor_role: str) -> list[PublicUser]:
        out = []
        for u in self.users.list_all():
            try:
                self._verify_user_mac(u)
                uname = self.enc.dec_pii(u.id, u.username_enc)
                role = self.enc.dec_pii(u.id, u.role_enc)
            except Exception:
                continue
            if actor_role != "admin" and u.id != actor.id and role == "admin":
                continue
            out.append(PublicUser(id=u.id, username=uname, role=role, is_active=u.is_active))
        return out

    def set_active(self, user_id: int, active: bool) -> None:
        user = self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("user not found")
        user.is_active = active
        self.db.commit()
