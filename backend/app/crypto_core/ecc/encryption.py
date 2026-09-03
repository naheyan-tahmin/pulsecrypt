"""
Hashed ElGamal over secp256k1 (asymmetric only).

For each message chunk m (integer < curve prime P):
    k  <- random in [1, n-1]
    C1  = k * G
    mask = (k * Q).x     # x-coordinate of ephemeral ECDH point
    C2  = (m + mask) mod P

Decryption: m = (C2 - (d * C1).x) mod P

No block cipher is used. Chunking lets us encrypt arbitrary-length
clinical notes. This is the algorithm applied to medical records so
that PII (RSA) and EHR posts (ECC) never share an encryption scheme.
"""

from __future__ import annotations
import secrets

from .curve import G, N, P, scalar_mult, point_to_bytes, point_from_bytes
from .keygen import ECPublicKey, ECPrivateKey

_CHUNK = 31  # stay strictly below 256-bit field prime


def encrypt(message: bytes, public_key: ECPublicKey) -> bytes:
    chunks = [message[i:i + _CHUNK] for i in range(0, max(len(message), 1), _CHUNK)]
    if not message:
        chunks = [b""]

    out = bytearray()
    out += len(chunks).to_bytes(4, "big")
    for chunk in chunks:
        m = int.from_bytes(chunk, "big")
        k = secrets.randbelow(N - 1) + 1
        c1 = scalar_mult(k, G)
        shared = scalar_mult(k, public_key.point)
        if shared.infinity:
            raise ValueError("degenerate ECDH point")
        c2 = (m + shared.x) % P
        out += point_to_bytes(c1)
        out += c2.to_bytes(32, "big")
        out += len(chunk).to_bytes(1, "big")
    return bytes(out)


def decrypt(ciphertext: bytes, private_key: ECPrivateKey) -> bytes:
    if len(ciphertext) < 4:
        raise ValueError("ciphertext too short")
    n_chunks = int.from_bytes(ciphertext[:4], "big")
    offset = 4
    plain = bytearray()
    for _ in range(n_chunks):
        if offset + 65 + 32 + 1 > len(ciphertext):
            raise ValueError("truncated ECC ciphertext")
        c1 = point_from_bytes(ciphertext[offset:offset + 65])
        offset += 65
        c2 = int.from_bytes(ciphertext[offset:offset + 32], "big")
        offset += 32
        chunk_len = ciphertext[offset]
        offset += 1
        shared = scalar_mult(private_key.d, c1)
        if shared.infinity:
            raise ValueError("degenerate ECDH point")
        m = (c2 - shared.x) % P
        if chunk_len == 0:
            chunk = b""
        else:
            chunk = m.to_bytes(_CHUNK, "big")[-chunk_len:]
        plain += chunk
    return bytes(plain)


def encrypt_str(message: str, public_key: ECPublicKey) -> bytes:
    return encrypt(message.encode("utf-8"), public_key)


def decrypt_str(ciphertext: bytes, private_key: ECPrivateKey) -> str:
    return decrypt(ciphertext, private_key).decode("utf-8")
