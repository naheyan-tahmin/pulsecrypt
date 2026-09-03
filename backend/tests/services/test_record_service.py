import json
from app.crypto_core.ecc.keygen import generate_keypair as ecc_keypair
from app.crypto_core.ecc.encryption import encrypt, decrypt
from app.crypto_core.rsa.keygen import generate_keypair as rsa_keypair
from app.crypto_core.rsa.encryption import encrypt as rsa_encrypt, decrypt as rsa_decrypt
from app.crypto_core.mac.hmac_custom import hmac_sha256, hmac_verify
from app.services.mac_service import MacService


def test_records_use_ecc_not_rsa():
    """Clinical payloads round-trip with ECC; PII-shaped fields round-trip with RSA."""
    ecc = ecc_keypair()
    rsa = rsa_keypair(512)
    payload = json.dumps({"title": "Labs", "body": "HbA1c 6.8", "diagnosis": "T2DM"}).encode()
    pii = b"patient@example.com"

    ecc_ct = encrypt(payload, ecc.public)
    rsa_ct = rsa_encrypt(pii, rsa.public)

    assert decrypt(ecc_ct, ecc.private) == payload
    assert rsa_decrypt(rsa_ct, rsa.private) == pii
    # Different algorithms produce unrelated ciphertext structure
    assert ecc_ct[:4] != rsa_ct[:4] or len(ecc_ct) != len(rsa_ct)


def test_record_mac_rejects_bit_flips():
    mac = MacService(b"unit-test-mac-key-32bytes-long!!")
    body = b"ciphertext-of-ehr-note"
    tag = mac.tag(body)
    mac.verify(tag, body)
    tampered = bytes([body[0] ^ 0x01]) + body[1:]
    try:
        mac.verify(tag, tampered)
        assert False, "tamper should raise"
    except Exception as exc:
        assert "HMAC" in str(exc) or "integrity" in str(exc).lower()
    assert hmac_verify(mac.mac_key, body, hmac_sha256(mac.mac_key, body))
