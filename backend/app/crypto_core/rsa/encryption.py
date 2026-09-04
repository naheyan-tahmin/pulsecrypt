
from __future__ import annotations
import secrets

from .primitives import mod_pow
from .keygen import RSAPublicKey, RSAPrivateKey

# Padding scheme byte markers (PKCS#1 v1.5-style structure):
#   0x00 || 0x02 || PS (random nonzero bytes) || 0x00 || message
_PAD_LEADING = 0x00
_PAD_BLOCK_TYPE = 0x02
_MIN_PAD_LEN = 8  # minimum padding bytes for meaningful randomization


def _int_to_bytes(value: int, length: int) -> bytes:
    return value.to_bytes(length, byteorder="big")


def _bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big")


def _key_byte_length(n: int) -> int:
    return (n.bit_length() + 7) // 8


def _pad(message: bytes, block_size: int) -> bytes:
    """Apply randomized PKCS#1 v1.5-style padding to fit exactly block_size bytes."""
    max_message_len = block_size - 3 - _MIN_PAD_LEN
    if len(message) > max_message_len:
        raise ValueError(
            f"message chunk too long for key size: {len(message)} > {max_message_len}"
        )

    pad_len = block_size - 3 - len(message)
    padding = bytearray()
    while len(padding) < pad_len:
        b = secrets.randbits(8)
        if b != 0:  # padding bytes must be nonzero so the 0x00 terminator is unambiguous
            padding.append(b)

    return bytes([_PAD_LEADING, _PAD_BLOCK_TYPE]) + bytes(padding) + bytes([0x00]) + message


def _unpad(padded: bytes) -> bytes:
    if len(padded) < 3 or padded[0] != _PAD_LEADING or padded[1] != _PAD_BLOCK_TYPE:
        raise ValueError("invalid padding: bad header")

    # Find the 0x00 separator after the random padding bytes
    try:
        sep_index = padded.index(0x00, 2)
    except ValueError:
        raise ValueError("invalid padding: no separator found")

    return padded[sep_index + 1:]


def _chunk_plain_size(block_size: int) -> int:
    return block_size - 3 - _MIN_PAD_LEN


def encrypt(message: bytes, public_key: RSAPublicKey) -> bytes:
   
    block_size = _key_byte_length(public_key.n)
    plain_chunk_size = _chunk_plain_size(block_size)

    if plain_chunk_size <= 0:
        raise ValueError("RSA key too small to encrypt any data with this padding scheme")

    chunks = [message[i:i + plain_chunk_size] for i in range(0, len(message), plain_chunk_size)]
    if not chunks:
        chunks = [b""]  # allow encrypting an empty message

    output = bytearray()
    output += len(chunks).to_bytes(4, byteorder="big")

    for chunk in chunks:
        padded = _pad(chunk, block_size)
        m_int = _bytes_to_int(padded)
        c_int = mod_pow(m_int, public_key.e, public_key.n)
        output += _int_to_bytes(c_int, block_size)

    return bytes(output)


def decrypt(ciphertext: bytes, private_key: RSAPrivateKey) -> bytes:
    """Decrypt data produced by encrypt(), reversing the chunking and padding."""
    block_size = _key_byte_length(private_key.n)

    if len(ciphertext) < 4:
        raise ValueError("ciphertext too short to contain a chunk count")

    num_chunks = int.from_bytes(ciphertext[:4], byteorder="big")
    body = ciphertext[4:]

    if len(body) != num_chunks * block_size:
        raise ValueError("ciphertext length does not match declared chunk count")

    plaintext = bytearray()
    for i in range(num_chunks):
        block = body[i * block_size:(i + 1) * block_size]
        c_int = _bytes_to_int(block)
        m_int = mod_pow(c_int, private_key.d, private_key.n)
        padded = _int_to_bytes(m_int, block_size)
        plaintext += _unpad(padded)

    return bytes(plaintext)


def encrypt_str(message: str, public_key: RSAPublicKey) -> bytes:
    return encrypt(message.encode("utf-8"), public_key)


def decrypt_str(ciphertext: bytes, private_key: RSAPrivateKey) -> str:
    return decrypt(ciphertext, private_key).decode("utf-8")