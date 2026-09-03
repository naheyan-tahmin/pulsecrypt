# PulseCrypt architecture

## Layers

```
React UI  →  FastAPI routers  →  services  →  crypto_core + repositories  →  PostgreSQL
```

Routers are thin. Only `services/` may call `crypto_core`. Repositories persist ciphertext and MAC tags; they never encrypt.

## Encryption flow (PII vs EHR)

```
Registration / profile update
  plaintext fields
       │
       ▼
  user RSA public key  ── RSA encrypt (chunked, randomized padding)
       │
       ▼
  users.*_enc + HMAC(pii concatenation)

EHR create / edit
  {title, body, diagnosis} JSON
       │
       ▼
  owner ECC public key  ── hashed ElGamal on secp256k1
       │
       ▼
  medical_records.payload_enc + HMAC(ciphertext)
```

Passwords never enter RSA/ECC: `salt || iterated PulseHash(password)`.

## Key management

On first boot the server generates a **master RSA** keypair (`data/master_rsa.json`). Each user gets:

- RSA keypair (PII)
- ECC keypair (records)

Private keys are wrapped with the master RSA public key (`private_key_enc`) and MAC’d. Rotation decrypts existing rows with the old keys, generates new pairs, re-encrypts, and deactivates the previous `key_records` versions.

## Doctor–patient share

```
Patient                Server                 Doctor
   │  DH start (p,g,A)   │
   │────────────────────►│
   │                     │  pending exchange
   │                     │◄────────────────── accept (B)
   │                     │  s = g^{ab} mod p
   │                     │  store H(s) only
   │  share(record, dh)  │
   │────────────────────►│ decrypt with patient ECC
   │                     │ re-encrypt with doctor ECC
   │                     │ MAC tag for share row
```

The DH shared secret authorizes the channel; clinical bytes are still ECC-encrypted to the recipient (asymmetric-only storage).

## Session flow

```
login(password) → pre2fa token
verify TOTP     → active token

token = Base64( RSA_encrypt( {sub,sid,exp,stage} )  ||  HMAC-SHA256 )
```

Each request: decode → verify HMAC → RSA decrypt → check expiry, revocation, and `stage=active`. Stolen cookies that fail the MAC are rejected.

## RBAC

| Role | Can |
|---|---|
| patient | own profile, own records, initiate/share via DH |
| doctor | own profile, notes, accept DH, read shares |
| admin | list users, enable/disable, rotate keys (not bulk-export of chart plaintext) |
