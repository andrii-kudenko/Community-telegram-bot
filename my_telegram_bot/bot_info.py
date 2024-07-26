from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, MessageEntityType
from aiogram.types import BotCommandScopeChat, BotCommand

BOT_TOKEN = '7204463589:AAE9yBSac6cpQQW6hHGD3ItkndJ8cmMoYMY'
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def set_commands(commands, id):
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=id))

async def set_default_commands(id):
    await bot.set_my_commands(default_commands, scope=BotCommandScopeChat(chat_id=id))

async def set_back_commands(id):
    await bot.set_my_commands(back_commands, scope=BotCommandScopeChat(chat_id=id))

back_commands = [
    BotCommand(command="/back", description="Go back"),
    BotCommand(command="/cancel", description="Cancel process"),
    BotCommand(command="/home", description="Go gome"),
]

default_commands = [BotCommand(command="/start", description="Start bot"), 
                    BotCommand(command="/help", description="Get help"),
                    BotCommand(command="/home", description="Go home"), 
                    BotCommand(command="/friends", description="Look for friends"),
                    ]