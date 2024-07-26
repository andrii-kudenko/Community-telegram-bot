from typing import Any
from aiogram import Dispatcher, Router, html, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
import markups.markups as nav
import random

from geopy.geocoders import Nominatim
def get_country_name(latitude, longitude):
    geolocator = Nominatim(user_agent="andrew")
    location = geolocator.reverse((latitude, longitude), language='en')
    address = location.raw['address']
    road = address.get('road', 'Unknown')
    city = address.get('city', 'Unknown')
    country = address.get('country', 'Unknown')
    return (road, city, country)

BOT_TOKEN = '7346863259:AAFZLxh1tggUDOyWRDb5Tv0K9TRWSDB_kCM'
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

message_router = Router(name=__name__)

@message_router.message()
async def bot_message(message: Message) -> None:
    if message.text == 'Random number':
        await bot.send_message(message.from_user.id, 'Your number is: ' + str(random.randint(1000, 9999)))
    elif message.text == 'Get Compliment':
        try:
            user_profile_photos = await bot.get_user_profile_photos(user_id=message.from_user.id)
            print("Got photos")
            if user_profile_photos.total_count > 0:
                print("More than 0")
                # Get the most recent profile photo
                photo = user_profile_photos.photos[0][-1]  # Get the highest resolution of the most recent photo
                print("Obtained photo")
                await bot.send_photo(chat_id=message.chat.id, photo=photo.file_id)
                await bot.send_message(chat_id=message.chat.id, text="So hey, sweetie)")
            else:
                await message.answer("You don't have any profile photos.")
        except:
            await bot.send_message(chat_id=message.chat.id, text="Error number 2")
    
    # --- MENU ---

    elif message.text == 'Main Menu':
        await bot.send_message(message.from_user.id, 'Main menu...', reply_markup=nav.mainMenu)
    elif message.text == 'Jobs':
        await bot.send_message(message.from_user.id, 'Jobs...', reply_markup=nav.methodChoiceMenu)
    elif message.text == 'Livings':
        await bot.send_message(message.from_user.id, 'Livings...', reply_markup=nav.methodChoiceMenu)
    elif message.text == 'Sales':
        await bot.send_message(message.from_user.id, 'Sales...', reply_markup=nav.methodChoiceMenu)
    elif message.text == 'Friends':
        await bot.send_message(message.from_user.id, 'Friends...', reply_markup=nav.methodChoiceMenu)



    elif message.text == 'Get info':
        await bot.send_message(message.from_user.id, 'Some info')
    elif message.text == 'Get text':
        await bot.send_message(message.from_user.id, 'Some text')
    elif message.text == 'Get Location':
        await bot.send_message(message.from_user.id, 'Some text')

    # ----- -----

    elif message.location:    
        print(message.location.latitude, message.location.longitude)
        user_location = get_country_name(message.location.latitude, message.location.longitude)
        print(f"The country is: {user_location[2]}")
        await bot.send_message(message.from_user.id, f'Nice, {user_location[2]} is a vey good Country! Also, {user_location[1]} is a very good city, and {user_location[0]} is a fantastic street')
    else:
        # info = await bot.get_me()
        # print(info.id)
        # await message.reply('Uknown command')
        # await message.answer_contact(phone_number='16477815562', first_name='Valera', last_name='Ronaldinho')
        my_message = await message.answer(text='Hello')
        await my_message.edit_text(text='Hello again')

@message_router.callback_query()
async def bot_query(callback_query: CallbackQuery) -> None:
    me = FSInputFile("me_hi.jpg")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=me, caption="Hello! It's me")
    # if callback_query.data == "jobs":
    #     await callback_query.answer("Button clicked!")
    #     user_id = callback_query.from_user.id
    #     await bot.send_message(text="You clicked Jobs!", chat_id=user_id, reply_markup=nav.navigationMenu)
    #     await bot.send_message(text="What do you want to do?", chat_id=user_id, reply_markup=nav.methodChoiceMenu)
    # else:
    #     await callback_query.answer("Invalid query!")
