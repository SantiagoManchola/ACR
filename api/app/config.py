"""Configuración del API ACR (pydantic-settings).

Lee variables de entorno desde `.env` (ubicado en la carpeta `api/`).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "mysql+pymysql://acr_user:acr_password@localhost:3306/acr"
    jwt_secret: str = "cambia-este-secreto-en-produccion"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    refresh_token_expire_days: int = 7
    cors_origins: str = "*"
    admin_username: str = "admin"
    admin_password: str = "admin123"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
