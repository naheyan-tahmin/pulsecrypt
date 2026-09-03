# PulseCrypt algorithms (from scratch)

Nothing in `backend/app/crypto_core` imports framework crypto (`hashlib`, `hmac`, `cryptography`, `PyJWT`, `pyotp`). Tests may use the standard library only as a correctness oracle.

## RSA (`crypto_core/rsa`)

- Prime generation: random odd `k`-bit candidates + Miller–Rabin (`is_probable_prime`, 40 rounds).
- Keygen: `n = pq`, `e = 65537`, `d = e⁻¹ mod φ(n)` via extended Euclid.
- Encryption: PKCS#1 v1.5-style type-2 padding (random non-zero PS), then `c = mᵉ mod n` with square-and-multiply (`mod_pow`).
- Long messages: 4-byte chunk count plus fixed-width blocks.

Used for **PII** (name, email, phone, NID, profile demographics) and for **wrapping** user private keys and session payloads under the server master key.

## ECC (`crypto_core/ecc`)

Curve: **secp256k1** (`y² = x³ + 7` over a 256-bit prime field). Point add / double / double-and-add scalar multiply are implemented in affine coordinates.

**Hashed ElGamal (asymmetric, no AES):**

- Ephemeral `k`, `C1 = kG`, `mask = (kQ)_x`, `C2 = (m + mask) mod p`.
- Decrypt: `m = (C2 − (d·C1)_x) mod p`.
- 31-byte chunks so `m < p`.

Used for **medical records** so clinical data never shares RSA with demographics.

## Diffie–Hellman (`crypto_core/diffie_hellman`)

- Generate prime `p` (Miller–Rabin) and generator `g`.
- `A = gᵃ mod p`, `B = gᵇ mod p`, `s = Bᵃ = Aᵇ mod p`.
- Store `SHA-256(s)` as the channel authenticator. Record sharing then **re-encrypts** the note to the peer’s ECC public key (still asymmetric).

## Hashing (`crypto_core/hashing`)

Merkle–Damgård **SHA-256** and **SHA-1** implemented from FIPS 180 (compress, Σ/σ rotations, K constants). Project name: PulseHash = SHA-256.

Password storage: `iterations $ hex(salt) $ hex(digest)` with `digest = H^i (salt || password)`.

## MAC (`crypto_core/mac`)

- **HMAC** (RFC 2104) over SHA-1 and SHA-256 (`ipad`/`opad`).
- **CBC-MAC** over a 16-byte Feistel network keyed by PulseHash expansion — integrity only, never used to encrypt stored fields.

HMAC-SHA256 tags bind user PII bundles, profiles, records, key blobs, DH transcripts, and session tokens.

## TOTP (`crypto_core/totp`)

RFC 6238: `HOTP(secret, floor(unix / 30))` using HMAC-SHA1 dynamic truncation, 6 digits, ±1 step window. Compatible with authenticator apps (`otpauth://` SHA1).

## Sessions

Active access requires password **and** TOTP. The bearer token is RSA-encrypted JSON plus a 32-byte HMAC. Server-side `token_hash` allows revocation.
