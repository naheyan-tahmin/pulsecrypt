from app.crypto_core.hashing.custom_hash import sha256
from app.crypto_core.hashing.password_hash import hash_password_for_storage, verify_password
from app.crypto_core.totp.totp import generate_secret, totp_at, verify_totp, provisioning_uri


def username_hash(username: str) -> str:
    return sha256(username.strip().lower().encode("utf-8")).hex()


def test_username_hash_is_stable_and_case_insensitive():
    assert username_hash("Alice") == username_hash(" alice ")
    assert username_hash("alice") != username_hash("bob")


def test_password_never_stored_in_plaintext():
    stored = hash_password_for_storage("SuperSecret1", iterations=200)
    assert "SuperSecret1" not in stored
    assert stored.count("$") == 2
    assert verify_password("SuperSecret1", stored)
    assert not verify_password("SuperSecret2", stored)


def test_totp_second_factor_window():
    secret = generate_secret()
    code = totp_at(secret, timestamp=1_700_000_000)
    assert verify_totp(secret, code, timestamp=1_700_000_000)
    assert not verify_totp(secret, "000000", timestamp=1_700_000_000)
    uri = provisioning_uri(secret, "alice")
    assert uri.startswith("otpauth://totp/PulseCrypt:alice")
