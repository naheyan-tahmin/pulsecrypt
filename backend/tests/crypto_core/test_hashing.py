import hashlib
from app.crypto_core.hashing.custom_hash import sha256, sha1, pulse_hash
from app.crypto_core.hashing.password_hash import hash_password_for_storage, verify_password


def test_sha256_matches_reference():
    cases = [b"", b"abc", b"PulseCrypt" * 20]
    for msg in cases:
        assert sha256(msg) == hashlib.sha256(msg).digest()
        assert pulse_hash(msg) == hashlib.sha256(msg).digest()


def test_sha1_matches_reference():
    for msg in [b"", b"abc", b"totp-secret"]:
        assert sha1(msg) == hashlib.sha1(msg).digest()


def test_password_salt_and_verify():
    stored = hash_password_for_storage("correct horse", iterations=500)
    assert verify_password("correct horse", stored)
    assert not verify_password("wrong", stored)
    stored2 = hash_password_for_storage("correct horse", iterations=500)
    assert stored != stored2
