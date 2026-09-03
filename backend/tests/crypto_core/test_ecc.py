from app.crypto_core.ecc.curve import G, N, scalar_mult, point_add, is_on_curve, INF
from app.crypto_core.ecc.keygen import generate_keypair
from app.crypto_core.ecc.encryption import encrypt, decrypt, encrypt_str, decrypt_str


def test_generator_on_curve():
    assert is_on_curve(G)


def test_scalar_mult_order():
    assert scalar_mult(N, G) == INF
    assert scalar_mult(1, G) == G
    assert is_on_curve(scalar_mult(2, G))


def test_point_add_commutative_small():
    p2 = scalar_mult(2, G)
    p3 = scalar_mult(3, G)
    assert point_add(p2, G) == p3


def test_ecc_roundtrip():
    kp = generate_keypair()
    msg = b'{"title":"Dx","body":"Type 2 diabetes follow-up"}'
    ct = encrypt(msg, kp.public)
    assert decrypt(ct, kp.private) == msg


def test_ecc_empty_and_unicode():
    kp = generate_keypair()
    assert decrypt(encrypt(b"", kp.public), kp.private) == b""
    text = "Diagnosis: fièvre — HbA1c 7.2%"
    assert decrypt_str(encrypt_str(text, kp.public), kp.private) == text
