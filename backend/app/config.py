from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "PulseCrypt"
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = "postgresql+psycopg2://pulsecrypt:pulsecrypt@localhost:5432/pulsecrypt"

    rsa_key_bits: int = 1024
    dh_prime_bits: int = 512
    password_iterations: int = 20_000

    session_lifetime_seconds: int = 8 * 3600
    pre2fa_lifetime_seconds: int = 300

    master_key_path: str = "data/master_rsa.json"

    admin_username: str = "admin"
    admin_password: str = "Admin123!"
    admin_email: str = "admin@pulsecrypt.local"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
