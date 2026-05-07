from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/recipemind"
    )
    GEMINI_API_KEY: str = Field(default="")

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        # Some providers still use "postgres://", SQLAlchemy expects "postgresql://"
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
