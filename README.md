# PulseCrypt

End-to-end encrypted EHR portal: custom RSA for PII, custom ECC for clinical notes, salted PulseHash passwords, TOTP 2FA, HMAC/CBC-MAC integrity, Diffie–Hellman doctor–patient sharing, and RBAC.

## Stack

- React (Vite) frontend
- FastAPI backend
- PostgreSQL

Cryptography lives only in `backend/app/crypto_core/`. Services call that package; routers never import primitives. There are no `hashlib` / `hmac` / `cryptography` / `PyJWT` / `pyotp` imports inside `crypto_core` (tests may compare against stdlib as an oracle).

**Run locally:** see [setup.md](setup.md).

## Algorithm split

| Data | Algorithm |
|---|---|
| Name, email, phone, NID, profile | RSA (from scratch, PKCS#1 v1.5-style padding) |
| EHR posts / diagnoses | ECC hashed-ElGamal on secp256k1 |
| Passwords | Salted iterative SHA-256 (PulseHash) |
| Integrity | HMAC-SHA256 + CBC-MAC (Feistel) |
| 2FA | RFC 6238 TOTP over HMAC-SHA1 |
| Sessions | RSA-encrypted payload + HMAC |
| Sharing | Custom Diffie–Hellman, then ECC re-encrypt for the recipient |

See `docs/algorithms.md` and `docs/architecture.md`.
