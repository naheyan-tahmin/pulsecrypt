from app.crypto_core.diffie_hellman.dh import (
    generate_params,
    generate_keypair,
    derive_shared_secret,
    shared_secret_digest,
)


def test_dh_shared_secret_agreement():
    params = generate_params(256)
    alice = generate_keypair(params)
    bob = generate_keypair(params)
    s1 = derive_shared_secret(params, alice.private, bob.public)
    s2 = derive_shared_secret(params, bob.private, alice.public)
    assert s1 == s2
    assert shared_secret_digest(s1) == shared_secret_digest(s2)
    assert s1 != alice.public
