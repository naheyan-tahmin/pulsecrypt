

from __future__ import annotations

from ..hashing.custom_hash import sha1, sha256

_HASHES = {
    "sha256": (sha256, 64, 32),
    "sha1": (sha1, 64, 20),
}


def hmac(key: bytes, message: bytes, hash_name: str = "sha256") -> bytes:
    if hash_name not in _HASHES:
        raise ValueError(f"unsupported hash: {hash_name}")
    digest_fn, block_size, _ = _HASHES[hash_name]

    if len(key) > block_size:
        key = digest_fn(key)
    key = key.ljust(block_size, b"\x00")

    ipad = bytes(b ^ 0x36 for b in key)
    opad = bytes(b ^ 0x5C for b in key)
    return digest_fn(opad + digest_fn(ipad + message))


def hmac_sha256(key: bytes, message: bytes) -> bytes:
    return hmac(key, message, "sha256")


def hmac_sha1(key: bytes, message: bytes) -> bytes:
    return hmac(key, message, "sha1")


def hmac_verify(key: bytes, message: bytes, tag: bytes, hash_name: str = "sha256") -> bool:
    actual = hmac(key, message, hash_name)
    if len(actual) != len(tag):
        return False
    acc = 0
    for a, b in zip(actual, tag):
        acc |= a ^ b
    return acc == 0
