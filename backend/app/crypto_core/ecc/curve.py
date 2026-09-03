"""
secp256k1 curve arithmetic over GF(p): point add, double, scalar multiply.

All operations are written with elementary modular arithmetic — no
cryptography libraries.
"""

from __future__ import annotations
from dataclasses import dataclass

# secp256k1
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8


def _egcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r = a, b
    old_s, s = 1, 0
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    return old_r, old_s, 0


def modinv(a: int, m: int = P) -> int:
    a %= m
    g, x, _ = _egcd(a, m)
    if g != 1:
        raise ValueError("no inverse")
    return x % m


@dataclass(frozen=True)
class Point:
    x: int
    y: int
    infinity: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        if self.infinity and other.infinity:
            return True
        if self.infinity or other.infinity:
            return False
        return self.x == other.x and self.y == other.y


INF = Point(0, 0, infinity=True)
G = Point(GX, GY)


def is_on_curve(pt: Point) -> bool:
    if pt.infinity:
        return True
    return (pt.y * pt.y - (pt.x ** 3 + A * pt.x + B)) % P == 0


def point_add(p1: Point, p2: Point) -> Point:
    if p1.infinity:
        return p2
    if p2.infinity:
        return p1
    if p1.x == p2.x and (p1.y + p2.y) % P == 0:
        return INF

    if p1.x == p2.x and p1.y == p2.y:
        if p1.y % P == 0:
            return INF
        lam = (3 * p1.x * p1.x + A) * modinv(2 * p1.y, P) % P
    else:
        lam = (p2.y - p1.y) * modinv(p2.x - p1.x, P) % P

    x3 = (lam * lam - p1.x - p2.x) % P
    y3 = (lam * (p1.x - x3) - p1.y) % P
    return Point(x3, y3)


def point_neg(pt: Point) -> Point:
    if pt.infinity:
        return pt
    return Point(pt.x, (-pt.y) % P)


def scalar_mult(k: int, pt: Point) -> Point:
    if k % N == 0 or pt.infinity:
        return INF
    if k < 0:
        return scalar_mult(-k, point_neg(pt))

    result = INF
    addend = pt
    kk = k
    while kk:
        if kk & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        kk >>= 1
    return result


def point_to_bytes(pt: Point) -> bytes:
    if pt.infinity:
        return b"\x00" * 65
    return b"\x04" + pt.x.to_bytes(32, "big") + pt.y.to_bytes(32, "big")


def point_from_bytes(data: bytes) -> Point:
    if len(data) != 65 or data[0] != 0x04:
        if data == b"\x00" * 65:
            return INF
        raise ValueError("invalid uncompressed point")
    pt = Point(int.from_bytes(data[1:33], "big"), int.from_bytes(data[33:65], "big"))
    if not is_on_curve(pt):
        raise ValueError("point is not on secp256k1")
    return pt
