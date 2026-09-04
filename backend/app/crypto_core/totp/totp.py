from __future__ import annotations
import secrets
import time
import base64

from ..mac.hmac_custom import hmac_sha1

DIGITS = 6
PERIOD = 30
SECRET_BYTES = 20


def generate_secret() -> bytes:
    return secrets.token_bytes(SECRET_BYTES)


def secret_to_base32(secret: bytes) -> str:
    return base64.b32encode(secret).decode("ascii").rstrip("=")


def secret_from_base32(encoded: str) -> bytes:
    pad = "=" * ((8 - len(encoded) % 8) % 8)
    return base64.b32decode(encoded.upper() + pad)


def hotp(secret: bytes, counter: int, digits: int = DIGITS) -> str:
    counter_bytes = counter.to_bytes(8, "big")
    digest = hmac_sha1(secret, counter_bytes)
    offset = digest[-1] & 0x0F
    binary = (
        ((digest[offset] & 0x7F) << 24)
        | ((digest[offset + 1] & 0xFF) << 16)
        | ((digest[offset + 2] & 0xFF) << 8)
        | (digest[offset + 3] & 0xFF)
    )
    otp = binary % (10 ** digits)
    return str(otp).zfill(digits)


def totp_at(secret: bytes, timestamp: float | None = None, digits: int = DIGITS, period: int = PERIOD) -> str:
    if timestamp is None:
        timestamp = time.time()
    counter = int(timestamp) // period
    return hotp(secret, counter, digits)


def verify_totp(
    secret: bytes,
    code: str,
    timestamp: float | None = None,
    window: int = 1,
    digits: int = DIGITS,
    period: int = PERIOD,
) -> bool:
    if timestamp is None:
        timestamp = time.time()
    code = (code or "").strip()
    if not code.isdigit() or len(code) != digits:
        return False
    counter = int(timestamp) // period
    for delta in range(-window, window + 1):
        if hotp(secret, counter + delta, digits) == code:
            return True
    return False


def provisioning_uri(secret: bytes, account: str, issuer: str = "PulseCrypt") -> str:
    b32 = secret_to_base32(secret)
    return (
        f"otpauth://totp/{issuer}:{account}"
        f"?secret={b32}&issuer={issuer}&algorithm=SHA1&digits={DIGITS}&period={PERIOD}"
    )
