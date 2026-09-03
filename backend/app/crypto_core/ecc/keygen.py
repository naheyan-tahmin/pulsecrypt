"""EC keypair generation on secp256k1."""

from __future__ import annotations
import secrets
from dataclasses import dataclass

from .curve import G, N, Point, scalar_mult, point_to_bytes, point_from_bytes


@dataclass(frozen=True)
class ECPublicKey:
    point: Point

    def to_bytes(self) -> bytes:
        return point_to_bytes(self.point)

    @classmethod
    def from_bytes(cls, data: bytes) -> "ECPublicKey":
        return cls(point_from_bytes(data))


@dataclass(frozen=True)
class ECPrivateKey:
    d: int

    def to_bytes(self) -> bytes:
        return self.d.to_bytes(32, "big")

    @classmethod
    def from_bytes(cls, data: bytes) -> "ECPrivateKey":
        d = int.from_bytes(data, "big")
        if not (1 <= d < N):
            raise ValueError("invalid EC private scalar")
        return cls(d=d)


@dataclass(frozen=True)
class ECKeyPair:
    public: ECPublicKey
    private: ECPrivateKey


def generate_keypair() -> ECKeyPair:
    d = secrets.randbelow(N - 1) + 1
    pub = scalar_mult(d, G)
    return ECKeyPair(public=ECPublicKey(pub), private=ECPrivateKey(d))
