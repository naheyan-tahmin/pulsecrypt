from __future__ import annotations
import json
from pathlib import Path

from sqlalchemy.orm import Session

from ..config import settings
from ..crypto_core.rsa.keygen import generate_keypair as generate_rsa, RSAKeyPair, RSAPublicKey, RSAPrivateKey
from ..crypto_core.ecc.keygen import generate_keypair as generate_ecc, ECKeyPair
from ..crypto_core.rsa.encryption import encrypt as rsa_encrypt, decrypt as rsa_decrypt
from ..crypto_core.key_manager.key_store import (
    serialize_rsa_private,
    deserialize_rsa_private,
    serialize_rsa_public,
    deserialize_rsa_public,
    serialize_ecc_public,
    deserialize_ecc_public,
    wrap_rsa_private,
    unwrap_rsa_private,
    wrap_ecc_private,
    unwrap_ecc_private,
)
from ..crypto_core.key_manager.rotation import rotate_rsa, rotate_ecc
from ..crypto_core.hashing.custom_hash import sha256
from ..crypto_core.diffie_hellman.dh import (
    generate_params,
    generate_keypair as dh_generate_keypair,
    derive_shared_secret,
    shared_secret_digest,
    params_to_dict,
    params_from_dict,
    DHParams,
)
from ..models.key_record import KeyRecord, DhExchange
from ..models.user import User
from ..models.patient_profile import PatientProfile
from ..models.medical_record import MedicalRecord
from ..repositories.key_repository import KeyRepository
from ..crypto_core.rsa.encryption import encrypt as rsa_encrypt_bytes, decrypt as rsa_decrypt_bytes
from ..crypto_core.ecc.encryption import encrypt as ecc_encrypt_bytes, decrypt as ecc_decrypt_bytes
from ..services.mac_service import MacService
from ..core.exceptions import NotFoundError, ForbiddenError, AuthError
from ..utils.encoding import b64e, b64d


class MasterKeys:
    def __init__(self, pair: RSAKeyPair, mac_key: bytes):
        self.pair = pair
        self.mac_key = mac_key


def load_or_create_master() -> MasterKeys:
    path = Path(settings.master_key_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        priv = deserialize_rsa_private(bytes.fromhex(data["private"]))
        pub = deserialize_rsa_public(bytes.fromhex(data["public"]))
        pair = RSAKeyPair(public=pub, private=priv)
    else:
        pair = generate_rsa(settings.rsa_key_bits)
        path.write_text(
            json.dumps(
                {
                    "public": serialize_rsa_public(pair.public).hex(),
                    "private": serialize_rsa_private(pair.private).hex(),
                }
            ),
            encoding="utf-8",
        )
    mac_key = sha256(b"pulsecrypt-mac-v1" + serialize_rsa_private(pair.private))
    return MasterKeys(pair, mac_key)


_MASTER: MasterKeys | None = None


def get_master() -> MasterKeys:
    global _MASTER
    if _MASTER is None:
        _MASTER = load_or_create_master()
    return _MASTER


class KeyService:
    def __init__(self, db: Session, master: MasterKeys | None = None):
        self.db = db
        self.repo = KeyRepository(db)
        self.master = master or get_master()
        self.mac = MacService(self.master.mac_key)

    def issue_user_keys(self, user_id: int) -> None:
        rsa_kp = generate_rsa(settings.rsa_key_bits)
        ecc_kp = generate_ecc()
        self._store_rsa(user_id, rsa_kp, version=1)
        self._store_ecc(user_id, ecc_kp, version=1)

    def _store_rsa(self, user_id: int, kp: RSAKeyPair, version: int) -> KeyRecord:
        wrapped = wrap_rsa_private(kp.private, self.master.pair.public)
        pub = serialize_rsa_public(kp.public)
        rec = KeyRecord(
            user_id=user_id,
            key_type="rsa",
            version=version,
            public_key=pub,
            private_key_enc=wrapped,
            is_active=1,
            mac_tag=b"",
        )
        rec.mac_tag = self.mac.tag(pub, wrapped, str(version).encode())
        return self.repo.add(rec)

    def _store_ecc(self, user_id: int, kp: ECKeyPair, version: int) -> KeyRecord:
        wrapped = wrap_ecc_private(kp.private, self.master.pair.public)
        pub = serialize_ecc_public(kp.public)
        rec = KeyRecord(
            user_id=user_id,
            key_type="ecc",
            version=version,
            public_key=pub,
            private_key_enc=wrapped,
            is_active=1,
            mac_tag=b"",
        )
        rec.mac_tag = self.mac.tag(pub, wrapped, str(version).encode())
        return self.repo.add(rec)

    def load_rsa(self, user_id: int) -> RSAKeyPair:
        rec = self.repo.active_for_user(user_id, "rsa")
        if not rec:
            raise NotFoundError("RSA key not found")
        self.mac.verify(rec.mac_tag, rec.public_key, rec.private_key_enc, str(rec.version).encode())
        priv = unwrap_rsa_private(rec.private_key_enc, self.master.pair.private)
        pub = deserialize_rsa_public(rec.public_key)
        return RSAKeyPair(public=pub, private=priv)

    def load_ecc(self, user_id: int) -> ECKeyPair:
        rec = self.repo.active_for_user(user_id, "ecc")
        if not rec:
            raise NotFoundError("ECC key not found")
        self.mac.verify(rec.mac_tag, rec.public_key, rec.private_key_enc, str(rec.version).encode())
        priv = unwrap_ecc_private(rec.private_key_enc, self.master.pair.private)
        pub = deserialize_ecc_public(rec.public_key)
        return ECKeyPair(public=pub, private=priv)

    def public_rsa(self, user_id: int) -> RSAPublicKey:
        return self.load_rsa(user_id).public

    def rotate_user_keys(self, user_id: int) -> dict:
        old_rsa = self.load_rsa(user_id)
        old_ecc = self.load_ecc(user_id)
        rsa_rec = self.repo.active_for_user(user_id, "rsa")
        ecc_rec = self.repo.active_for_user(user_id, "ecc")
        new_rsa = generate_rsa(settings.rsa_key_bits)
        new_ecc = generate_ecc()
        new_rsa_ver = rsa_rec.version + 1
        new_ecc_ver = ecc_rec.version + 1

        def rewrap_rsa(blob: bytes) -> bytes:
            if not blob or blob == b"\x00":
                return blob
            pt = rsa_decrypt_bytes(blob, old_rsa.private)
            return rsa_encrypt_bytes(pt, new_rsa.public)

        user = self.db.get(User, user_id)
        if user:
            user.username_enc = rewrap_rsa(user.username_enc)
            user.email_enc = rewrap_rsa(user.email_enc)
            user.phone_enc = rewrap_rsa(user.phone_enc)
            user.full_name_enc = rewrap_rsa(user.full_name_enc)
            user.national_id_enc = rewrap_rsa(user.national_id_enc)
            user.role_enc = rewrap_rsa(user.role_enc)
            user.totp_secret_enc = rewrap_rsa(user.totp_secret_enc)
            user.pii_mac = self.mac.tag(
                user.username_enc, user.email_enc, user.phone_enc,
                user.full_name_enc, user.national_id_enc, user.role_enc,
            )
        profile = self.db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
        if profile:
            profile.address_enc = rewrap_rsa(profile.address_enc)
            profile.blood_type_enc = rewrap_rsa(profile.blood_type_enc)
            profile.date_of_birth_enc = rewrap_rsa(profile.date_of_birth_enc)
            profile.emergency_contact_enc = rewrap_rsa(profile.emergency_contact_enc)
            profile.mac_tag = self.mac.tag(
                profile.address_enc, profile.blood_type_enc,
                profile.date_of_birth_enc, profile.emergency_contact_enc,
            )
        records = self.db.query(MedicalRecord).filter(MedicalRecord.owner_id == user_id).all()
        for rec in records:
            self.mac.verify(rec.mac_tag, rec.payload_enc)
            pt = ecc_decrypt_bytes(rec.payload_enc, old_ecc.private)
            rec.payload_enc = ecc_encrypt_bytes(pt, new_ecc.public)
            rec.mac_tag = self.mac.tag(rec.payload_enc)

        rsa_rec.is_active = 0
        ecc_rec.is_active = 0
        self._store_rsa(user_id, new_rsa, new_rsa_ver)
        self._store_ecc(user_id, new_ecc, new_ecc_ver)
        self.db.commit()
        return {"rsa_version": new_rsa_ver, "ecc_version": new_ecc_ver}

    def start_dh(self, initiator_id: int, peer_id: int) -> DhExchange:
        params = generate_params(settings.dh_prime_bits)
        kp = dh_generate_keypair(params)
        wrapped_priv = rsa_encrypt(kp.private.to_bytes((kp.private.bit_length() + 7) // 8, "big"), self.master.pair.public)
        params_json = json.dumps(params_to_dict(params))
        ex = DhExchange(
            initiator_id=initiator_id,
            peer_id=peer_id,
            params_json=params_json,
            initiator_public=hex(kp.public),
            peer_public=None,
            initiator_private_enc=wrapped_priv,
            status="pending",
            mac_tag=b"",
        )
        ex.mac_tag = self.mac.tag(params_json.encode(), wrapped_priv, hex(kp.public).encode())
        return self.repo.add_dh(ex)

    def accept_dh(self, exchange_id: int, actor_id: int) -> DhExchange:
        ex = self.repo.get_dh(exchange_id)
        if not ex:
            raise NotFoundError("DH exchange not found")
        if ex.peer_id != actor_id:
            raise ForbiddenError("only the invited peer can accept this exchange")
        if ex.status != "pending":
            raise AuthError("exchange is not pending")
        params = params_from_dict(json.loads(ex.params_json))
        kp = dh_generate_keypair(params)
        wrapped_peer = rsa_encrypt(kp.private.to_bytes((kp.private.bit_length() + 7) // 8, "big"), self.master.pair.public)
        ex.peer_public = hex(kp.public)
        ex.peer_private_enc = wrapped_peer

        init_priv = int.from_bytes(rsa_decrypt(ex.initiator_private_enc, self.master.pair.private), "big")
        secret = derive_shared_secret(params, init_priv, kp.public)
        # Cross-check with peer private
        secret2 = derive_shared_secret(params, kp.private, int(ex.initiator_public, 16))
        if secret != secret2:
            raise AuthError("DH shared secrets did not match")
        ex.shared_secret_hash = shared_secret_digest(secret)
        ex.status = "complete"
        ex.mac_tag = self.mac.tag(ex.params_json.encode(), ex.shared_secret_hash)
        self.db.commit()
        return ex

    def require_complete_dh(self, exchange_id: int, user_a: int, user_b: int) -> DhExchange:
        ex = self.repo.get_dh(exchange_id)
        if not ex or ex.status != "complete":
            raise ForbiddenError("complete a Diffie-Hellman exchange before sharing records")
        parties = {ex.initiator_id, ex.peer_id}
        if {user_a, user_b} != parties:
            raise ForbiddenError("DH exchange does not match these users")
        if ex.shared_secret_hash:
            self.mac.verify(ex.mac_tag, ex.params_json.encode(), ex.shared_secret_hash)
        return ex
