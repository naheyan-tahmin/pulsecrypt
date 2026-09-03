from __future__ import annotations
import json

from sqlalchemy.orm import Session

from ..crypto_core.rsa.encryption import encrypt as rsa_encrypt, decrypt as rsa_decrypt
from ..crypto_core.ecc.encryption import encrypt as ecc_encrypt, decrypt as ecc_decrypt
from ..services.key_service import KeyService, get_master
from ..services.mac_service import MacService


class EncryptionService:
    """
    Orchestrates algorithm choice:
      - RSA  → user PII / profile demographics
      - ECC  → medical record payloads
    """

    def __init__(self, db: Session):
        self.keys = KeyService(db)
        self.mac = MacService(get_master().mac_key)

    def enc_pii(self, user_id: int, plaintext: str) -> bytes:
        kp = self.keys.load_rsa(user_id)
        return rsa_encrypt((plaintext or "").encode("utf-8"), kp.public)

    def dec_pii(self, user_id: int, ciphertext: bytes) -> str:
        if not ciphertext:
            return ""
        kp = self.keys.load_rsa(user_id)
        return rsa_decrypt(ciphertext, kp.private).decode("utf-8")

    def enc_record(self, owner_id: int, payload: dict) -> tuple[bytes, bytes]:
        kp = self.keys.load_ecc(owner_id)
        raw = json.dumps(payload).encode("utf-8")
        ct = ecc_encrypt(raw, kp.public)
        tag = self.mac.tag(ct)
        return ct, tag

    def dec_record(self, owner_id: int, ciphertext: bytes, tag: bytes) -> dict:
        self.mac.verify(tag, ciphertext)
        kp = self.keys.load_ecc(owner_id)
        raw = ecc_decrypt(ciphertext, kp.private)
        return json.loads(raw.decode("utf-8"))

    def enc_record_for(self, recipient_id: int, payload: dict) -> tuple[bytes, bytes]:
        kp = self.keys.load_ecc(recipient_id)
        raw = json.dumps(payload).encode("utf-8")
        ct = ecc_encrypt(raw, kp.public)
        tag = self.mac.tag(ct)
        return ct, tag

    def pii_mac(self, *ciphertexts: bytes) -> bytes:
        return self.mac.tag(*ciphertexts)
