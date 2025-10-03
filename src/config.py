import os

from dotenv import load_dotenv

load_dotenv()

BOT_API_KEY: str = os.getenv("BOT_API_KEY", default="")

assert BOT_API_KEY != "", "Bot api key should be added to the env variables"
