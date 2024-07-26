import logging 
import asyncio
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, UserProfilePhotos
# from aiogram.types.user_profile_photos import UserProfilePhotos
from aiogram.methods import SendMessage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.methods.send_media_group import SendMediaGroup
# from handlers.input_handler import echo_handler
from handlers.input_handler import register_command_handlers


BOT_TOKEN = '7346863259:AAFZLxh1tggUDOyWRDb5Tv0K9TRWSDB_kCM'
# Initialize Bot with default properties
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

dp.callback_query.middleware(CallbackAnswerMiddleware)

# Defining keyboard and adding buttons
# builder = InlineKeyboardBuilder()
# builder.button(text="Button 1", callback_data="button1")
# builder.button(text="Button 2", callback_data="button2")
# builder.button(text="Button 3", callback_data="button3")
# builder.button(text="Button 4", callback_data="button4")
# builder.adjust(3,2)


media_group = MediaGroupBuilder(caption="Media group caption")

# Add photo
media_group.add_photo(media="https://picsum.photos/200/300")
# Dynamically add photo with known type without using separate method
media_group.add(type="photo", media="https://picsum.photos/200/300")


# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
    
#     # await message.answer(f"Привiт, {html.bold(message.from_user.full_name)}! Я твiй помiчник Валерiй")
#     # await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
#     # await bot.send_media_group(chat_id=message.chat.id, )
#     print("I'm handling")

#     # Get user profile photos
#     user_profile_photos = await bot.get_user_profile_photos(user_id=message.from_user.id)
#     print("Got photos")
    
#     if user_profile_photos.total_count > 0:
#         print("More than 0")
#         # Get the most recent profile photo
#         photo = user_profile_photos.photos[0][-1]  # Get the highest resolution of the most recent photo
#         print("Obtained photo")
#         await bot.send_photo(chat_id=message.chat.id, photo=photo.file_id)
#     else:
#         await message.answer("You don't have any profile photos.")

register_command_handlers(dp, bot)

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



async def main() -> None:
    
    # And the run events dispatching
    try:
        # Start polling
        await dp.start_polling(bot)
    finally:
        # Ensure the bot is closed properly
        await bot.session.close()

    # await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    # asyncio.run(main())
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")