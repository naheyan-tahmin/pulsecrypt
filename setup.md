# PulseCrypt setup

Run the API and the React app on your machine. PostgreSQL must already be installed and running.

## 1. PostgreSQL

Create a database and user (pgAdmin or `psql`):

```sql
CREATE USER pulsecrypt WITH PASSWORD 'pulsecrypt';
CREATE DATABASE pulsecrypt OWNER pulsecrypt;
```

Default URL used by the backend:

```text
postgresql+psycopg2://pulsecrypt:pulsecrypt@localhost:5432/pulsecrypt
```

If your username, password, or database name is different, change `DATABASE_URL` in `backend/.env`.

## 2. Backend (FastAPI)

From the project root, in PowerShell:

```powershell
cd backend
copy .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

First start creates tables, a master RSA key at `backend/data/master_rsa.json`, and a seed admin. Admin TOTP secret is written to `backend/data/admin_totp.txt`.

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Seed login: `admin` / `Admin123!` plus the TOTP secret from `admin_totp.txt`

Leave this terminal running.

## 3. Frontend (React)

Open a second terminal:

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

Open http://localhost:5173

`frontend/.env` should contain:

```text
VITE_API_URL=http://localhost:8000
```

## 4. Try it

1. Register a **patient** and a **doctor** (or use admin after adding the TOTP secret to an authenticator app).
2. Complete the 6-digit 2FA step.
3. Create a medical record, start a Diffie–Hellman exchange on the dashboard, accept it from the other account, then share the record.

Registration is slow on purpose (from-scratch RSA key generation).

## Tests (optional)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```
