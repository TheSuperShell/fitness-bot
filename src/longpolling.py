import asyncio

from .bot import setup


async def main() -> None:
    dp, bot = setup()
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
