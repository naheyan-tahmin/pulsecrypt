import hashlib
from app.crypto_core.rsa.keygen import generate_keypair
from app.crypto_core.rsa.encryption import encrypt, decrypt, encrypt_str, decrypt_str


def test_rsa_roundtrip_bytes():
    kp = generate_keypair(512)
    msg = b"PulseCrypt PII: Alice Patient / +8801711000000"
    ct = encrypt(msg, kp.public)
    assert ct != msg
    assert decrypt(ct, kp.private) == msg


def test_rsa_randomized_ciphertext():
    kp = generate_keypair(512)
    msg = b"same plaintext"
    c1 = encrypt(msg, kp.public)
    c2 = encrypt(msg, kp.public)
    assert c1 != c2
    assert decrypt(c1, kp.private) == msg
    assert decrypt(c2, kp.private) == msg


def test_rsa_string_helpers():
    kp = generate_keypair(512)
    text = "NID-123456789"
    assert decrypt_str(encrypt_str(text, kp.public), kp.private) == text
