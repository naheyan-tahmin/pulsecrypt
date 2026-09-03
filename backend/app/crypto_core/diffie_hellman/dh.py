"""
Diffie–Hellman over a custom multiplicative group Z_p^*.

Parameters (p, g) are generated here (safe-enough prime search for the
assignment). Shared secret is g^(ab) mod p. The numeric secret is never
used as a symmetric cipher key for stored records; it authenticates a
doctor↔patient channel and is hashed with PulseHash for comparison.
"""

from __future__ import annotations
import secrets
from dataclasses import dataclass

from ..rsa.primitives import is_probable_prime, mod_pow
from ..hashing.custom_hash import sha256


def _generate_prime(bits: int) -> int:
    while True:
        n = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(n, rounds=16):
            return n


def find_generator(p: int) -> int:
    """Pick a small g whose order is not 1 (g^((p-1)/2) ≢ 1 is a practical check for odd primes)."""
    phi = p - 1
    for g in range(2, 100):
        if mod_pow(g, phi, p) != 1:
            continue
        if mod_pow(g, 2, p) == 1:
            continue
        if mod_pow(g, phi // 2, p) != 1:
            return g
    # fallback
    return 5


@dataclass(frozen=True)
class DHParams:
    p: int
    g: int
    bits: int


@dataclass
class DHKeyPair:
    params: DHParams
    private: int
    public: int


def generate_params(bits: int = 512) -> DHParams:
    """Generate DH modulus and generator. 512-bit default keeps lab keygen tractable."""
    p = _generate_prime(bits)
    g = find_generator(p)
    return DHParams(p=p, g=g, bits=bits)


def generate_keypair(params: DHParams) -> DHKeyPair:
    priv = secrets.randbelow(params.p - 3) + 2
    pub = mod_pow(params.g, priv, params.p)
    return DHKeyPair(params=params, private=priv, public=pub)


def derive_shared_secret(params: DHParams, my_private: int, peer_public: int) -> int:
    if peer_public <= 1 or peer_public >= params.p - 1:
        raise ValueError("invalid DH public value")
    return mod_pow(peer_public, my_private, params.p)


def shared_secret_digest(secret: int) -> bytes:
    return sha256(secret.to_bytes((secret.bit_length() + 7) // 8 or 1, "big"))


def params_to_dict(params: DHParams) -> dict:
    return {"p": hex(params.p), "g": hex(params.g), "bits": params.bits}


def params_from_dict(data: dict) -> DHParams:
    return DHParams(p=int(data["p"], 16), g=int(data["g"], 16), bits=int(data["bits"]))
