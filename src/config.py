from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    bot_api_key: str = ""
    db_account: str = ""
    db_user: str = ""
    db_password: str = ""
    db_database: str = ""

    weight_upper_limit: float = 500.0
    weight_lower_limit: float = 1.0
    height_upper_limit: float = 300.0
    height_lower_limit: float = 1.0

    google_timezone_api_key: str = ""

    web_url: str = ""
    webhook_path: str = "/bot"
    webhook_secret: str = ""

    @property
    def webhook_url(self) -> str:
        return f"{self.web_url}{self.webhook_path}"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_account}:5432/{self.db_database}"


config = Config()
