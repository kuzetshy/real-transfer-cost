from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/transfer_cost_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()