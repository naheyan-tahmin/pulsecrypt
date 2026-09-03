from __future__ import annotations

from ..crypto_core.mac.hmac_custom import hmac_sha256, hmac_verify
from ..crypto_core.mac.cbc_mac import cbc_mac, cbc_mac_verify
from ..core.exceptions import IntegrityError


class MacService:
    def __init__(self, mac_key: bytes):
        self.mac_key = mac_key

    def tag(self, *parts: bytes) -> bytes:
        return hmac_sha256(self.mac_key, b"|".join(parts))

    def verify(self, tag: bytes, *parts: bytes) -> None:
        if not hmac_verify(self.mac_key, b"|".join(parts), tag):
            raise IntegrityError("HMAC verification failed — data may have been tampered with")

    def cbc_tag(self, data: bytes) -> bytes:
        return cbc_mac(self.mac_key, data)

    def cbc_verify(self, data: bytes, tag: bytes) -> None:
        if not cbc_mac_verify(self.mac_key, data, tag):
            raise IntegrityError("CBC-MAC verification failed")
