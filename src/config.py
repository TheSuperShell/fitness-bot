from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    bot_api_key: str = ""
    db_account: str = ""
    db_user: str = ""
    db_password: str = ""
    db_database: str = ""

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_account}:5432/{self.db_database}"


config = Config()
