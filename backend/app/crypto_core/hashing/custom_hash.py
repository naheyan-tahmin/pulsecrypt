"""
From-scratch Merkle–Damgård hash functions.

This module does not import hashlib. SHA-1 is implemented because RFC 6238
TOTP authenticators expect HMAC-SHA1. SHA-256 (PulseHash-256) is the
workhorse for password stretching, HMAC-SHA256 integrity tags, and KDFs.
"""

from __future__ import annotations

# --- SHA-256 constants (FIPS 180-4) -----------------------------------------

_SHA256_K = (
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
)

_SHA256_IV = (
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
)

_SHA1_IV = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)

_MASK32 = 0xFFFFFFFF


def _rotr32(x: int, n: int) -> int:
    x &= _MASK32
    return ((x >> n) | (x << (32 - n))) & _MASK32


def _rotl32(x: int, n: int) -> int:
    x &= _MASK32
    return ((x << n) | (x >> (32 - n))) & _MASK32


def _pad_md(message: bytes, block_size: int = 64) -> bytes:
    """Merkle–Damgård length padding (SHA-1 / SHA-256 64-byte blocks)."""
    bit_len = len(message) * 8
    padded = message + b"\x80"
    # 8 bytes of length at the end; pad with zeros so total ≡ 56 (mod 64)
    pad_len = (block_size - 8 - (len(padded) % block_size)) % block_size
    padded += b"\x00" * pad_len
    padded += bit_len.to_bytes(8, "big")
    return padded


def _sha256_compress(state: list[int], block: bytes) -> None:
    w = [int.from_bytes(block[i * 4:(i + 1) * 4], "big") for i in range(16)]
    for i in range(16, 64):
        s0 = _rotr32(w[i - 15], 7) ^ _rotr32(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1 = _rotr32(w[i - 2], 17) ^ _rotr32(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w.append((w[i - 16] + s0 + w[i - 7] + s1) & _MASK32)

    a, b, c, d, e, f, g, h = state
    for i in range(64):
        s1 = _rotr32(e, 6) ^ _rotr32(e, 11) ^ _rotr32(e, 25)
        ch = (e & f) ^ ((~e) & g)
        temp1 = (h + s1 + ch + _SHA256_K[i] + w[i]) & _MASK32
        s0 = _rotr32(a, 2) ^ _rotr32(a, 13) ^ _rotr32(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        temp2 = (s0 + maj) & _MASK32
        h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & _MASK32, c, b, a, (temp1 + temp2) & _MASK32

    state[0] = (state[0] + a) & _MASK32
    state[1] = (state[1] + b) & _MASK32
    state[2] = (state[2] + c) & _MASK32
    state[3] = (state[3] + d) & _MASK32
    state[4] = (state[4] + e) & _MASK32
    state[5] = (state[5] + f) & _MASK32
    state[6] = (state[6] + g) & _MASK32
    state[7] = (state[7] + h) & _MASK32


def sha256(message: bytes) -> bytes:
    """SHA-256 digest (32 bytes), implemented from first principles."""
    state = list(_SHA256_IV)
    padded = _pad_md(message)
    for i in range(0, len(padded), 64):
        _sha256_compress(state, padded[i:i + 64])
    return b"".join(h.to_bytes(4, "big") for h in state)


def sha256_hex(message: bytes) -> str:
    return sha256(message).hex()


def _sha1_compress(state: list[int], block: bytes) -> None:
    w = [int.from_bytes(block[i * 4:(i + 1) * 4], "big") for i in range(16)]
    for i in range(16, 80):
        w.append(_rotl32(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1))

    a, b, c, d, e = state
    for i in range(80):
        if i < 20:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif i < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif i < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6
        temp = (_rotl32(a, 5) + f + e + k + w[i]) & _MASK32
        e, d, c, b, a = d, c, _rotl32(b, 30), a, temp

    state[0] = (state[0] + a) & _MASK32
    state[1] = (state[1] + b) & _MASK32
    state[2] = (state[2] + c) & _MASK32
    state[3] = (state[3] + d) & _MASK32
    state[4] = (state[4] + e) & _MASK32


def sha1(message: bytes) -> bytes:
    """SHA-1 digest (20 bytes), implemented from first principles for TOTP."""
    state = list(_SHA1_IV)
    padded = _pad_md(message)
    for i in range(0, len(padded), 64):
        _sha1_compress(state, padded[i:i + 64])
    return b"".join(h.to_bytes(4, "big") for h in state)


def pulse_hash(message: bytes) -> bytes:
    """Project-facing name for the primary custom hash (SHA-256 construction)."""
    return sha256(message)


def expand_bytes(seed: bytes, length: int) -> bytes:
    """Hash-based expander: H(seed||counter) concatenated until `length` bytes."""
    out = bytearray()
    counter = 0
    while len(out) < length:
        out += sha256(seed + counter.to_bytes(4, "big"))
        counter += 1
    return bytes(out[:length])
