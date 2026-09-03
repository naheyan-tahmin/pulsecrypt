from app.crypto_core.mac.hmac_custom import hmac_sha256, hmac_sha1, hmac_verify
from app.crypto_core.mac.cbc_mac import cbc_mac, cbc_mac_verify
from app.crypto_core.hashing.custom_hash import sha1
import hashlib
import hmac as std_hmac


def test_hmac_sha256_matches_stdlib():
    key, msg = b"server-mac-key", b"medical-record-ciphertext"
    assert hmac_sha256(key, msg) == std_hmac.new(key, msg, hashlib.sha256).digest()
    assert hmac_verify(key, msg, hmac_sha256(key, msg))
    assert not hmac_verify(key, msg, b"\x00" * 32)


def test_hmac_sha1_matches_stdlib():
    key, msg = b"totp", b"\x00" * 8
    assert hmac_sha1(key, msg) == std_hmac.new(key, msg, hashlib.sha1).digest()
    assert sha1(b"abc") == hashlib.sha1(b"abc").digest()


def test_cbc_mac_detects_tamper():
    key, msg = b"integrity-key", b"diagnosis: stable"
    tag = cbc_mac(key, msg)
    assert cbc_mac_verify(key, msg, tag)
    assert not cbc_mac_verify(key, msg + b"x", tag)
    assert cbc_mac(key, msg) == tag
