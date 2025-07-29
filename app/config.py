from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    ADMIN_ID: int

    class Config:
        env_file = ".env"

settings = Settings()