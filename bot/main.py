import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import config
from bot.handlers import language, menu, node, panel, start
from bot.middlewares.language import LanguageMiddleware


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.update.outer_middleware(LanguageMiddleware())

    dp.include_router(start.router)
    dp.include_router(node.router)
    dp.include_router(panel.router)
    dp.include_router(language.router)
    dp.include_router(menu.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
