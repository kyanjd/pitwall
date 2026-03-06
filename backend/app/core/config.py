import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_DB: str
    DATABASE_URL: str
    # DATABASE_URL_DOCKER: str

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ADMIN_SECRET: str = ""


settings = Settings()  # type: ignore

if __name__ == "__main__":
    print("DATABASE_URL:", settings.DATABASE_URL)
    print("secret", settings.SECRET_KEY)
