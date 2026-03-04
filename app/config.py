from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://climate:climate@localhost:5432/climate_tracker"
    ENVIRONMENT: str = "development"
    ANTHROPIC_API_KEY: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
