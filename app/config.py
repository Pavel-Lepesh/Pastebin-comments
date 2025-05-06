import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


env_file = ".env.test" if os.getenv("PYTEST_CURRENT_TEST") else ".env"


class Settings(BaseSettings):
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DB_NAME: str

    APP_HOST: str
    APP_PORT: int
    EXTERNAL_APP_PORT: int

    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(env_file=env_file)


settings = Settings()
