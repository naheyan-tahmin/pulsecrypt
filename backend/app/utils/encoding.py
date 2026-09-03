from __future__ import annotations
import base64


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


def utf8(data: str) -> bytes:
    return data.encode("utf-8")
