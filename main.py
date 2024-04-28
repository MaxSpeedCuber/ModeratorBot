import asyncio
import re
from contextlib import suppress
from typing import Any
from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest
import config
from datetime import datetime, timedelta
from pymorphy3 import MorphAnalyzer
from aiogram.enums import ParseMode
from string import punctuation
def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        return None
    match_ = re.match(r"(\d+)([a-z])", time_string.lower().strip())
    current_datetime = datetime.utcnow()
    if match_:
        value = int(match_.group(1))
        unit = match_.group(2)
        match unit:
            case "s":
                delta = timedelta(seconds=value)
            case "m":
                delta = timedelta(minutes=value)
            case "h":
                delta = timedelta(hours=value)
            case "d":
                delta = timedelta(days=value)
            case "w":
                delta = timedelta(weeks=value)
            case _:
                return None
        new_datetime = current_datetime + delta
        return new_datetime
    else:
        return None
router = Router()
router.message.filter(F.chat.type == "supergroup", F.from_user.id == 5030790426)
morph = MorphAnalyzer(lang="ru")
triggers = {"клоун", "еблан", "чурка", "мамаша", "сука", "пидор"}
@router.message(Command("ban"))
async def ban(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    reply = message.reply_to_message
    if not reply:
        await message.answer("Банить можно ТОЛЬКО ОТВЕТОМ НА СООБЩЕНИЯ!!!")
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)
    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=reply.from_user.id, until_date=until_date)
    await message.answer(f"<b>{mention}</b> был забанен за плохое поведение!! Не повторяйте его ошибок!!!", parse_mode=ParseMode.HTML)
@router.message(Command("mute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    reply = message.reply_to_message
    if not reply:
        await message.answer("Мьютить можно ТОЛЬКО ОТВЕТОМ НА СООБЩЕНИЯ!!!")
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)
    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=reply.from_user.id, until_date=until_date, permissions=ChatPermissions(can_send_messages=False))
    await message.answer(f"<b>{mention}</b> будет в муте за плохое поведение!! Не повторяйте его ошибок!!!", parse_mode=ParseMode.HTML)
def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))
@router.edited_message()
@router.message()
async def cleaner(message: Message):
    if triggers.intersection(clean_text(message.text.lower()).split()):
        await message.answer(f"<b>{message.from_user.first_name}</b>, не ругайся!!!", parse_mode=ParseMode.HTML)
        await message.delete()
async def main() -> None:
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(True)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())