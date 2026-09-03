"""
Number-theoretic primitives underlying RSA.

Nothing here calls into any external crypto library — only plain
integer arithmetic. These functions are the building blocks that
keygen.py and encryption.py rely on.
"""

from __future__ import annotations
import secrets


def gcd(a: int, b: int) -> int:
    """Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Returns (g, x, y) such that a*x + b*y = g = gcd(a, b).
    Implemented iteratively to avoid recursion-depth issues on large keys.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    return old_r, old_s, old_t


def mod_inverse(a: int, m: int) -> int:
    """
    Modular multiplicative inverse of a mod m, via extended Euclid.
    Raises ValueError if a and m are not coprime (inverse doesn't exist).
    """
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse modulo {m} (gcd = {g})")
    return x % m


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """
    Fast modular exponentiation via square-and-multiply.
    Equivalent to Python's built-in pow(base, exponent, modulus),
    implemented explicitly since RSA's core operation must be
    demonstrably from-scratch.
    """
    if modulus == 1:
        return 0
    result = 1
    base %= modulus
    exp = exponent
    while exp > 0:
        if exp & 1:
            result = (result * base) % modulus
        exp >>= 1
        base = (base * base) % modulus
    return result


def is_probable_prime(n: int, rounds: int = 40) -> bool:
    """
    Miller-Rabin probabilistic primality test.
    `rounds` controls confidence: probability of a false positive
    is at most 4^(-rounds). 40 rounds is far beyond what's needed
    for cryptographic-strength primes but is cheap relative to
    the key generation it gates.
    """
    if n in (2, 3):
        return True
    if n < 2 or n % 2 == 0:
        return False

    # Write n - 1 as 2^r * d with d odd
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2  # random witness in [2, n-2]
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = mod_pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True