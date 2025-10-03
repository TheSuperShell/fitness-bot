import os

from dotenv import load_dotenv

load_dotenv()

BOT_API_KEY: str = os.getenv("BOT_API_KEY", default="")

DB_ACCOUNT: str = os.getenv("DB_ACCOUNT", default="")
DB_USER: str = os.getenv("DB_USER", default="")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", default="")

DB_DATABASE: str = os.getenv("DB_DATABASE", default="bot")

assert BOT_API_KEY != "", "Bot api key should be added to the env variables"
assert DB_ACCOUNT != "", "add DB_ACCOUNT to the env variables"
assert DB_USER != "", "add DB_USER to the env variables"
assert DB_PASSWORD != "", "add DB_PASSWORD to the env variables"


def get_db_url() -> str:
    return (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_ACCOUNT}:5432/{DB_DATABASE}"
    )
