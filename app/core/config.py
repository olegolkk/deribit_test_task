from pydantic_settings import BaseSettings
from pydantic import BaseModel


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DataBaseConfig(BaseModel):
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "deribit"
    url: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


class DeribitAPI(BaseModel):
    url: str = "https://www.deribit.com/api/v2"


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    db: DataBaseConfig = DataBaseConfig()
    deribit: DeribitAPI = DeribitAPI()


settings = Settings()