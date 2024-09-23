import logging 
import asyncio
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, types, Router, F
from aiogram.fsm.scene import Scene, SceneRegistry, ScenesManager, on
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, MessageEntityType
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, ReplyKeyboardRemove,
                           UserProfilePhotos, BotDescription, Chat, FSInputFile, MessageEntity, CallbackQuery)
from aiogram.methods import SendMessage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.methods.send_media_group import SendMediaGroup
from aiogram.fsm.context import FSMContext
import markups.markups as nav
import random
# from handlers.message_handler import message_router
from handlers.friendships_handler.friendships_handler import friendship_router, start_friends_query
# from my_telegram_bot.handlers.friendships_handler.friendships_handler import friendship_router, start_friends_query
from handlers.sales_handler.sales_handler import sales_router, start_sales
# from my_telegram_bot.handlers.sales_handler.sales_handler import sales_router, start_sales
from handlers.jobs_handler.jobs_handler import job_router, start_jobs
# from my_telegram_bot.handlers.jobs_handler.jobs_handler import job_router, start_jobs
from handlers.livings_handler.livings_handler import living_router, start_livings
# from my_telegram_bot.handlers.livings_handler.livings_handler import living_router, start_livings
from handlers.empty_input_handler import empty_router
from home import home_router
from bot_info import bot as bot
from bot_info import set_back_commands, set_default_commands

from database.models import init_db, SessionLocal
from database.requests import add_user, get_user

async def get_db():
    async with SessionLocal() as session:
        yield session

dp = Dispatcher()
main_router = Router(name=__name__)
dp.include_routers(main_router, home_router, sales_router, job_router, 
                   living_router, friendship_router, empty_router)

@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:    
    async for db in get_db():
        user = await get_user(db, message.from_user.id)
        if user is None:
            user = await add_user(db, message.from_user.id, message.from_user.full_name)
            await message.reply(f"Welcome, {message.from_user.full_name}")
        else:
            await message.reply(f"Welcome back, {message.from_user.full_name}")

    # await message.reply_markup(reply_markup=ReplyKeyboardRemove())
    me = FSInputFile("me_hi.jpg")
    await message.answer_photo(photo=me, caption="Hi, it's me!")
    await message.answer(f"Привiт, {html.bold(message.from_user.full_name)}! Я твiй помiчник {html.underline("Андрiй")}\nЩоб ти хотiв зробити зараз?", reply_markup=nav.categoryChoiceMenu.as_markup())
    
# @dp.message(Command("home", prefix=("!/")))
# async def home(message: Message) -> None:
#     await message.answer("Home Menu", reply_markup=ReplyKeyboardRemove())
#     await message.answer("Choose category: egwvwvwvabrbebre", reply_markup=nav.categoryChoiceMenu.as_markup())
#     # my_message = await message.answer("Home")
#     # print(my_message)
#     # print(my_message.message_id)
#     # await bot.edit_message_text(message_id=my_message.message_id, chat_id=my_message.chat.id, text="Choose a category:", reply_markup=nav.categoryChoiceMenu.as_markup())
#     # await bot.edit_message_reply_markup()
#     # await message.edit_text(inline_message_id=my_message.message_id, text="Choose a category:", reply_markup=nav.categoryChoiceMenu.as_markup())
#     # await message.answer("Choose a category:", reply_markup=nav.categoryChoiceMenu.as_markup())
#     await set_default_commands(id=message.from_user.id)

@main_router.message(Command("help", prefix=("!/")))
async def help(message: Message) -> None:
    await message.answer("Help menu", reply_markup=ReplyKeyboardRemove())
    await set_default_commands(id=message.from_user.id)

@main_router.callback_query(nav.ChoiceCallback.filter())
async def choice_query(query: CallbackQuery, callback_data: nav.ChoiceCallback, state: FSMContext):
    if callback_data.func == "jobs":
        await query.answer("Jobs Finder")
        await query.message.edit_text("Jobs 💻")
        await start_jobs(query.message, state)
    if callback_data.func == "livings":
        await query.answer("Livings Finder")
        await query.message.edit_text("Livings 🛏")
        await start_livings(query.message, state)
    if callback_data.func == "sales":
        await query.answer("Enter Sales")
        await query.message.edit_text("Sales 💵")
        await start_sales(query.message, state)
    if callback_data.func == "friends":
        await query.answer("Friends Finder")
        await query.message.edit_text("Friends 🤼")
        await start_friends_query(query, state)


    # bot.send_message(chat_id=query.from_user.id, text="HEllo")
    # user_id = query.from_user.id
    # message = Message(
    #     message_id=query.message.message_id,
    #     from_user=query.from_user,
    #     chat=query.message.chat,
    #     text='/friends'
    # )
    # message.answer()

async def main() -> None:
    await init_db()
    try:
        await bot.set_my_commands(commands=[BotCommand(command="/start", description="Start bot"),
                              BotCommand(command="/home", description="Go home"),
                              BotCommand(command="/jobs", description="Look for job"),
                              BotCommand(command="/friends", description="Look for friends"),
                              BotCommand(command="/help", description="Get help")
                              ])
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")














# @router1.message()
# async def bot_message(message: Message) -> None:
#     if message.text == 'Random number':
#         await bot.send_message(message.from_user.id, 'Your number is: ' + str(random.randint(1000, 9999)))
#     elif message.text == 'Get Compliment':
#         try:
#             user_profile_photos = await bot.get_user_profile_photos(user_id=message.from_user.id)
#             print("Got photos")
#             if user_profile_photos.total_count > 0:
#                 print("More than 0")
#                 # Get the most recent profile photo
#                 photo = user_profile_photos.photos[0][-1]  # Get the highest resolution of the most recent photo
#                 print("Obtained photo")
#                 await bot.send_photo(chat_id=message.chat.id, photo=photo.file_id)
#                 await bot.send_message(chat_id=message.chat.id, text="So hey, sweetie)")
#             else:
#                 await message.answer("You don't have any profile photos.")
#         except:
#             await bot.send_message(chat_id=message.chat.id, text="Error number 2")
#     elif message.text == 'Main Menu':
#         await bot.send_message(message.from_user.id, 'Main menu...', reply_markup=nav.mainMenu)
#     elif message.text == 'More Functions':
#         await bot.send_message(message.from_user.id, 'Extra menu...')
#     elif message.text == 'Get info':
#         await bot.send_message(message.from_user.id, 'Some info')
#     elif message.text == 'Get text':
#         await bot.send_message(message.from_user.id, 'Some text')
#     elif message.text == 'Get Location':
#         await bot.send_message(message.from_user.id, 'Some text')
#     # elif message.text == 'Invoice':
#     #     await message.reply_invoice(title='Shit', description="Grandad's shit", )
#     # elif message.location:
        
#     #     print(message.location.latitude, message.location.longitude)
#     #     user_location = get_country_name(message.location.latitude, message.location.longitude)
#     #     print(f"The country is: {user_location[2]}")
#     #     await bot.send_message(message.from_user.id, f'Nice, {user_location[2]} is a vey good Country! Also, {user_location[1]} is a very good city, and {user_location[0]} is a fantastic street')
#     else:
#         # info = await bot.get_me()
#         # print(info.id)
#         # await message.reply('Uknown command')
#         # await message.answer_contact(phone_number='16477815562', first_name='Valera', last_name='Ronaldinho')
#         my_message = await message.answer(text='Hello')
#         await my_message.edit_text(text='Hello again')


# @dp.message()
# async def echo_handler(message: Message) -> None:
#     # await SendMessage(chat_id=message.from_user.id, text=message.text)

#     try:
#         # await message.answer(message.text, reply_markup=builder.as_markup())
#         # await bot.send_message(chat_id=message.chat.id, text=UserProfilePhotos.total_count)
#         # Get user profile photos

#         user_profile_photos = await bot.get_user_profile_photos(user_id=message.from_user.id)
#         print("Got photos")
        
#         if user_profile_photos.total_count > 0:
#             print("More than 0")
#             # Get the most recent profile photo
#             photo = user_profile_photos.photos[0][-1]  # Get the highest resolution of the most recent photo
#             print("Obtained photo")
#             await bot.send_photo(chat_id=message.chat.id, photo=photo.file_id)
#             await bot.send_message(chat_id=message.chat.id, text="Ну здравствуй, красавчик)")
#         else:
#             await message.answer("You don't have any profile photos.")
#     except:
#         await bot.send_message(chat_id=message.chat.id, text="Error number 2")
#         # await message.answer_sticker(sticker=message.sticker.file_id)

#     await message.answer_dice()


    # try:
    #     # Send copy of the recieved message
    #     await message.send_copy(chat_id=message.chat.id)
    # except TypeError:
    #     # Not all the types are supported to be copied
    #     await message.answer("Nice try!")

