from __future__ import annotations
import json

from ..rsa.encryption import encrypt as rsa_encrypt, decrypt as rsa_decrypt
from ..rsa.keygen import RSAPublicKey, RSAPrivateKey, RSAKeyPair
from ..ecc.keygen import ECPublicKey, ECPrivateKey, ECKeyPair


def serialize_rsa_private(key: RSAPrivateKey) -> bytes:
    payload = {"n": hex(key.n), "d": hex(key.d), "p": hex(key.p), "q": hex(key.q)}
    return json.dumps(payload).encode("utf-8")


def deserialize_rsa_private(data: bytes) -> RSAPrivateKey:
    payload = json.loads(data.decode("utf-8"))
    return RSAPrivateKey(
        n=int(payload["n"], 16),
        d=int(payload["d"], 16),
        p=int(payload["p"], 16),
        q=int(payload["q"], 16),
    )


def serialize_rsa_public(key: RSAPublicKey) -> bytes:
    return json.dumps({"n": hex(key.n), "e": hex(key.e)}).encode("utf-8")


def deserialize_rsa_public(data: bytes) -> RSAPublicKey:
    payload = json.loads(data.decode("utf-8"))
    return RSAPublicKey(n=int(payload["n"], 16), e=int(payload["e"], 16))


def serialize_ecc_private(key: ECPrivateKey) -> bytes:
    return key.to_bytes()


def deserialize_ecc_private(data: bytes) -> ECPrivateKey:
    return ECPrivateKey.from_bytes(data)


def serialize_ecc_public(key: ECPublicKey) -> bytes:
    return key.to_bytes()


def deserialize_ecc_public(data: bytes) -> ECPublicKey:
    return ECPublicKey.from_bytes(data)


def wrap_private_blob(blob: bytes, master_public: RSAPublicKey) -> bytes:
    """Encrypt a private-key blob at rest under the server master RSA key."""
    return rsa_encrypt(blob, master_public)


def unwrap_private_blob(wrapped: bytes, master_private: RSAPrivateKey) -> bytes:
    return rsa_decrypt(wrapped, master_private)


def wrap_rsa_private(key: RSAPrivateKey, master_public: RSAPublicKey) -> bytes:
    return wrap_private_blob(serialize_rsa_private(key), master_public)


def unwrap_rsa_private(wrapped: bytes, master_private: RSAPrivateKey) -> RSAPrivateKey:
    return deserialize_rsa_private(unwrap_private_blob(wrapped, master_private))


def wrap_ecc_private(key: ECPrivateKey, master_public: RSAPublicKey) -> bytes:
    return wrap_private_blob(serialize_ecc_private(key), master_public)


def unwrap_ecc_private(wrapped: bytes, master_private: RSAPrivateKey) -> ECPrivateKey:
    return deserialize_ecc_private(unwrap_private_blob(wrapped, master_private))


def rsa_keypair_from_parts(public: RSAPublicKey, private: RSAPrivateKey) -> RSAKeyPair:
    return RSAKeyPair(public=public, private=private)


def ecc_keypair_from_parts(public: ECPublicKey, private: ECPrivateKey) -> ECKeyPair:
    return ECKeyPair(public=public, private=private)
