"""
Key rotation policy: bump version, keep previous wrapped keys until
re-encrypted fields are migrated. Callers persist the new KeyRecord.
"""

from __future__ import annotations
from dataclasses import dataclass

from ..rsa.keygen import generate_keypair as generate_rsa, RSAKeyPair
from ..ecc.keygen import generate_keypair as generate_ecc, ECKeyPair


@dataclass
class RotationResult:
    version: int
    previous_version: int
    rsa: RSAKeyPair | None = None
    ecc: ECKeyPair | None = None


def next_version(current: int) -> int:
    return current + 1


def rotate_rsa(current_version: int) -> tuple[int, RSAKeyPair]:
    return next_version(current_version), generate_rsa()


def rotate_ecc(current_version: int) -> tuple[int, ECKeyPair]:
    return next_version(current_version), generate_ecc()
