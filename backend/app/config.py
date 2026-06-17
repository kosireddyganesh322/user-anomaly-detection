from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/anomaly_db"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
