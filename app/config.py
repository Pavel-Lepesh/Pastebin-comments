from pydantic_settings import BaseSettings, SettingsConfigDict
import os


env_file = (
    ".env.test" if os.getenv("PYTEST_CURRENT_TEST") else ".env"
)


class Settings(BaseSettings):
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DB_NAME: str

    model_config = SettingsConfigDict(env_file=env_file)


settings = Settings()
