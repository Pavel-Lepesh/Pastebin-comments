from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DB_NAME: str

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
