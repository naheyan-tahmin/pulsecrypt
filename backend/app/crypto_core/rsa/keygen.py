"""
RSA key pair generation.

Generates two large primes p and q, derives n = p*q, phi(n),
and a (public, private) exponent pair. All arithmetic goes through
primitives.py — no library primality testing or modexp.
"""

from __future__ import annotations
import secrets
from dataclasses import dataclass

from .primitives import gcd, mod_inverse, is_probable_prime

DEFAULT_PUBLIC_EXPONENT = 65537  # standard choice: small, coprime to most phi(n), fast to exponentiate with


@dataclass(frozen=True)
class RSAPublicKey:
    n: int
    e: int


@dataclass(frozen=True)
class RSAPrivateKey:
    n: int
    d: int
    # p, q, and CRT-derived params are kept for potential CRT speedups later;
    # not required for correctness of the basic scheme.
    p: int
    q: int


@dataclass(frozen=True)
class RSAKeyPair:
    public: RSAPublicKey
    private: RSAPrivateKey


def _generate_prime(bit_length: int) -> int:
   
    if bit_length < 2:
        raise ValueError("bit_length must be >= 2")

    while True:
        candidate = secrets.randbits(bit_length)
        # Force the top bit (so the number has the full requested bit length)
        # and the bottom bit (so it's odd).
        candidate |= (1 << (bit_length - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


def generate_keypair(key_size_bits: int = 2048) -> RSAKeyPair:
    
    if key_size_bits < 512:
        raise ValueError("key_size_bits should be at least 512 for any real use")

    half = key_size_bits // 2
    e = DEFAULT_PUBLIC_EXPONENT

    while True:
        p = _generate_prime(half)
        q = _generate_prime(half)
        if p == q:
            continue

        n = p * q
        phi = (p - 1) * (q - 1)

        if gcd(e, phi) != 1:
            # Extremely rare with e = 65537, but retry cleanly if it happens.
            continue

        d = mod_inverse(e, phi)

        return RSAKeyPair(
            public=RSAPublicKey(n=n, e=e),
            private=RSAPrivateKey(n=n, d=d, p=p, q=q),
        )