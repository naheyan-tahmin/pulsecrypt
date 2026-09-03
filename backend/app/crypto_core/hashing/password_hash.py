"""
Salted iterative password hashing built only on custom_hash.sha256.

Scheme:  salt || ITER(sha256, salt || password)
Stored form is hex(salt) + "$" + hex(digest) so the DB never holds a
password or an unsalted hash.
"""

from __future__ import annotations
import secrets

from .custom_hash import sha256

DEFAULT_ITERATIONS = 50_000
SALT_LEN = 16
DIGEST_LEN = 32


def generate_salt(length: int = SALT_LEN) -> bytes:
    return secrets.token_bytes(length)


def hash_password(password: str, salt: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    block = salt + password.encode("utf-8")
    digest = sha256(block)
    for _ in range(iterations - 1):
        digest = sha256(salt + digest)
    return digest


def encode_stored(salt: bytes, digest: bytes, iterations: int = DEFAULT_ITERATIONS) -> str:
    return f"{iterations}${salt.hex()}${digest.hex()}"


def decode_stored(stored: str) -> tuple[int, bytes, bytes]:
    parts = stored.split("$")
    if len(parts) != 3:
        raise ValueError("malformed stored password hash")
    iterations = int(parts[0])
    return iterations, bytes.fromhex(parts[1]), bytes.fromhex(parts[2])


def hash_password_for_storage(password: str, iterations: int = DEFAULT_ITERATIONS) -> str:
    salt = generate_salt()
    digest = hash_password(password, salt, iterations)
    return encode_stored(salt, digest, iterations)


def verify_password(password: str, stored: str) -> bool:
    try:
        iterations, salt, expected = decode_stored(stored)
    except (ValueError, TypeError):
        return False
    actual = hash_password(password, salt, iterations)
    if len(actual) != len(expected):
        return False
    acc = 0
    for a, b in zip(actual, expected):
        acc |= a ^ b
    return acc == 0
