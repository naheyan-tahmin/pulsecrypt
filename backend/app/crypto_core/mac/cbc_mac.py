"""
CBC-MAC over a from-scratch 128-bit Feistel block cipher.

This cipher is used only as a MAC primitive (integrity), never as a
storage encryption algorithm — stored fields use RSA or ECC only.
"""

from __future__ import annotations

from ..hashing.custom_hash import sha256, expand_bytes

BLOCK = 16
ROUNDS = 8


def _feistel_round_f(half: bytes, round_key: bytes) -> bytes:
    mixed = sha256(half + round_key)
    return mixed[:8]


def _expand_key(key: bytes) -> list[bytes]:
    material = expand_bytes(sha256(key), ROUNDS * 8)
    return [material[i * 8:(i + 1) * 8] for i in range(ROUNDS)]


def _encrypt_block(block: bytes, round_keys: list[bytes]) -> bytes:
    if len(block) != BLOCK:
        raise ValueError("block must be 16 bytes")
    left, right = block[:8], block[8:]
    for rk in round_keys:
        left, right = right, bytes(a ^ b for a, b in zip(left, _feistel_round_f(right, rk)))
    return left + right


def _pad_iso7816(data: bytes) -> bytes:
    padded = data + b"\x80"
    if len(padded) % BLOCK == 0:
        return padded
    return padded + b"\x00" * (BLOCK - (len(padded) % BLOCK))


def cbc_mac(key: bytes, message: bytes) -> bytes:
    """16-byte CBC-MAC tag."""
    round_keys = _expand_key(key)
    padded = _pad_iso7816(message)
    prev = bytes(BLOCK)
    for i in range(0, len(padded), BLOCK):
        block = padded[i:i + BLOCK]
        xored = bytes(a ^ b for a, b in zip(prev, block))
        prev = _encrypt_block(xored, round_keys)
    return prev


def cbc_mac_verify(key: bytes, message: bytes, tag: bytes) -> bool:
    actual = cbc_mac(key, message)
    if len(actual) != len(tag):
        return False
    acc = 0
    for a, b in zip(actual, tag):
        acc |= a ^ b
    return acc == 0
