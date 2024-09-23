from typing import Any, Dict
import logging

from aiogram import Router, F, html
from aiogram.utils import markdown
from aiogram.utils.markdown import bold, italic, text, code, pre
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, InputMediaPhoto, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from . import livings_markup as nav
from utils import location
from bot_info import set_back_commands, set_default_commands
from database import livings_requests as rq
from database.models import SessionLocal

living_router = Router(name=__name__)

class NewLiving():
    def __init__(self, user_id, username, description, price, city, address) -> None:
        self.user_id = user_id
        self.username = username
        self.description = description
        self.price = price
        self.city = city
        self.address = address

class Livings(StatesGroup):
    choice = State()
    searching = State()

class Living(StatesGroup):
    description = State()
    photo1 = State()
    photo2 = State()
    photo3 = State()
    photo4 = State()
    photo5 = State()
    photo6 = State()
    price = State()
    location = State()
    # optional
    address = State()

# ---UTILITY FUNCTIONS---
search_funcitons_map = { # execute appropriate function depending on the city_search value in bio
    True: rq.get_next_living_with_city,
    False: rq.get_next_living_without_city
}

@living_router.message(Command("livings", prefix=("!/")))
async def start_livings(message: Message, state: FSMContext):
    await state.set_state(Livings.choice)
    await message.answer("Hi there! Choose the action:", reply_markup=nav.livingsReplyChoiceMenu)

@living_router.message(Living.description, Command("cancel", prefix=("!/")))
@living_router.message(Living.price, Command("cancel", prefix=("!/")))
@living_router.message(Living.location, Command("cancel", prefix=("!/")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.set_state(Livings.choice)
    await message.answer(
        "Cancelled",
        reply_markup=nav.livingsChoiceMenu,
    )
    await set_default_commands(id=message.from_user.id)

@living_router.message(Living.description, Command("back", prefix=("!/")))
@living_router.message(Living.price, Command("back", prefix=("!/")))
@living_router.message(Living.location, Command("back", prefix=("!/")))
async def back_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Living.description:
            await state.set_state(Livings.choice)
            await message.answer("Choose action:", reply_markup=nav.livingsReplyChoiceMenu)
    elif current_state == Living.price:
            await state.set_state(Living.description)
            await message.answer("Send me new description")
    elif current_state == Living.location:
            await state.set_state(Living.price)
            await message.answer("Send me new price")


# --- SEARCH ---
@living_router.message(Livings.choice, F.text == "Search 🔎")
async def search(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # database call
    async with SessionLocal() as session:
        await rq.update_my_livings_city_search(session, user_id, True)
    await message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Livings.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        living, photos = await rq.get_next_living_with_city(session, user.livings_search_id_list, user.city)
        if living:
            summary = await living_summary(living, photos)
            await message.answer_media_group(media=summary)
            await rq.add_id_to_user_livings_search_id_list(session, user.user_id, living.id)
            # updated = await rq.add_id_to_user_sales_jobs_search_id_list()
        elif living is None:
            await message.answer("No more livings options", reply_markup=ReplyKeyboardRemove())
            await message.answer("Would you like to search for livings outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())
        else:
            await message.answer("No more livings posts", reply_markup=ReplyKeyboardRemove())
            await message.answer("You can come later to see new available livings options", reply_markup=nav.livingsChoiceMenu.as_markup())
@living_router.callback_query(nav.MenuCallback.filter(F.menu == "livings_go_search_beyond"))
async def search_beyond_by_query(query: CallbackQuery, state: FSMContext):
    await query.answer("Searching outside")
    user_id = query.from_user.id
    async with SessionLocal() as session:
        await rq.update_my_livings_city_search(session, user_id, False)
    await query.message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Livings.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        living, photos = await rq.get_next_living_without_city(session, user.livings_search_id_list, user.city)
        if living:
            summary = await living_summary(living, photos)
            await query.message.answer_media_group(media=summary)
            await rq.add_id_to_user_livings_search_id_list(session, user.user_id, living.id)
        else:
            await query.message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available sales options", reply_markup=nav.livingsChoiceMenu.as_markup()) 


# --- MY POSTS ---
@living_router.message(Livings.choice, F.text == "View my living ads 🧾")
async def my_living_posts_by_message(message: Message, state: FSMContext):
    # make a database request
    # and further manipulations
    async with SessionLocal() as session:
        new_job = await rq.test_add_job_post_to_user(session)
        print(new_job)
    await message.answer("My posts")
@living_router.callback_query(nav.MenuCallback.filter(F.menu == "my_livings"))
async def my_living_posts_by_query(query: CallbackQuery, state: FSMContext):
    # make a database request
    # and further manipulations
    async with SessionLocal() as session:
        new_job = await rq.test_add_job_post_to_user(session)
        print(new_job)
    await query.message.answer("My posts")


# --- NEW LIVING ---
@living_router.message(Livings.choice, F.text == "Post an ad 📰")
async def living(message: Message, state: FSMContext):
    username = message.from_user.username
    if username is None:
        await message.answer("You need to have a username for you account. \nGo to telegram settings and add a username")
        return
    await message.answer("Creating your ad...\
                         \nMind that you can always \nGo /back or /cancel the process")
    await state.set_state(Living.description)
    await message.answer("Provide a full description for your ad:", reply_markup=ReplyKeyboardRemove())
    await set_back_commands(id=message.from_user.id)

# @living_router.message(Livings.choice)
# async def choice_invalid(message: Message):
#     await message.answer("I don't understand you. Please choose your action or Go /home")
# @living_router.message(Living.title, F.text)
# async def living_title(message: Message, state: FSMContext):
#     await state.update_data(title=message.text)
#     await state.set_state(Living.description)
#     await message.answer(f"Now, provide some description:")


# --- LIVING CREATION ---
@living_router.message(Living.description, F.text)
async def living_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Living.photo1)
    await message.answer(f"Ok, now you can upload up to 6 photos for your ad:")
@living_router.message(Living.photo1, F.photo)
async def ad_photo1(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo1 = file_id)
    await state.set_state(Living.photo2)
    await message.answer("Nice, you have uploaded one photo. Send another one or just continue with this one", reply_markup=nav.photosUploadingReplyMenu1)
@living_router.message(Living.photo2, F.photo)
async def ad_photo2(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo3 = file_id)
    await state.set_state(Living.photo3)
    await message.answer("Good, now you have 2 photos. Add more?", reply_markup=nav.photosUploadingReplyMenu2)
@living_router.message(Living.photo3, F.photo)
async def ad_photo2(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo4 = file_id)
    await state.set_state(Living.photo4)
    await message.answer("Good, now you have 3 photos. Add more?", reply_markup=nav.photosUploadingReplyMenu3)
@living_router.message(Living.photo4, F.photo)
async def ad_photo2(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo5 = file_id)
    await state.set_state(Living.photo5)
    await message.answer("Good, now you have 4 photos. Add more?", reply_markup=nav.photosUploadingReplyMenu4)
@living_router.message(Living.photo5, F.photo)
async def ad_photo2(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo6 = file_id)
    await state.set_state(Living.photo5)
    await message.answer("Good, now you have 5 photos. Add more?", reply_markup=nav.photosUploadingReplyMenu5)
@living_router.message(Living.photo6, F.photo)
async def ad_photo3(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo6 = file_id)
    # await state.set_state(Living.photo6)
    await message.answer("Cool, now you have 6 photos for you ad", reply_markup=ReplyKeyboardRemove())
    await confirm_photos(message, state)
@living_router.message(Living.photo2, F.text == "Continue with 1/6 photos")
@living_router.message(Living.photo3, F.text == "Continue with 2/6 photos")
@living_router.message(Living.photo4, F.text == "Continue with 3/6 photos")
@living_router.message(Living.photo5, F.text == "Continue with 4/6 photos")
@living_router.message(Living.photo6, F.text == "Continue with 5/6 photos")
async def confirm_photos(message: Message, state: FSMContext):
    await state.set_state(Living.price)
    await message.answer(f"Ok, now provide price for your ad:", reply_markup=ReplyKeyboardRemove())
@living_router.message(Living.price, F.text)
async def living_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(Living.location)
    await message.answer(f"Ok, now provide the city for your place:", reply_markup=nav.locationMenu)
@living_router.message(Living.location, F.location)
async def living_location(message: Message, state: FSMContext):
    user_location = location.get_location(message.location.latitude, message.location.longitude)
    print(user_location)
    await state.update_data(location=user_location[1])
    data = await state.update_data(address=user_location[0])
    new_living = NewLiving(message.from_user.id, message.from_user.username, data["description"], data["price"], data["location"], data["address"])
    await state.clear()
    await show_summary(message=message, data=data)
    # make database request to add post
    async with SessionLocal() as session:
        photos = []
        photos.append(data["photo1"])  
        photos.append(data.get("photo2")) if data.get("photo2") else None
        photos.append(data.get("photo3")) if data.get("photo3") else None
        photos.append(data.get("photo4")) if data.get("photo4") else None
        photos.append(data.get("photo5")) if data.get("photo5") else None
        photos.append(data.get("photo6")) if data.get("photo6") else None
        new_living_post = await rq.add_living_to_user_by_id(session, new_living, photos)
        print("Living post added successfully", new_living_post)

    await state.set_state(Livings.choice)
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.livingsReplyChoiceMenu)
    await set_default_commands(id=message.from_user.id)
@living_router.message(Living.location, F.text)
async def living_city(message: Message, state: FSMContext):
    city = message.text.strip().capitalize()
    await state.update_data(location=city)
    await state.set_state(Living.address)
    await message.answer("Add an address (street) for your post")
@living_router.message(Living.address, F.text)
async def living_address(message: Message, state: FSMContext):
    data = await state.update_data(address=message.text)
    new_living = NewLiving(message.from_user.id, message.from_user.username, data["description"], data["price"], data["location"], data["address"])
    await state.clear()
    await show_summary(message=message, data=data)
    # make database request to add post
    async with SessionLocal() as session:
        photos = []
        photos.append(data["photo1"])  
        photos.append(data.get("photo2")) if data.get("photo2") else None
        photos.append(data.get("photo3")) if data.get("photo3") else None
        photos.append(data.get("photo4")) if data.get("photo4") else None
        photos.append(data.get("photo5")) if data.get("photo5") else None
        photos.append(data.get("photo6")) if data.get("photo6") else None
        new_living_post = await rq.add_living_to_user_by_id(session, new_living, photos)
        print("Living post added successfully", new_living_post)

    await state.set_state(Livings.choice)
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.livingsReplyChoiceMenu)

async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
    description = data["description"]
    price = data["price"]
    location = data["location"]
    address = data["address"]
    photos = []
    photos.append(data["photo1"])  
    photos.append(data.get("photo2")) if data.get("photo2") else None
    photos.append(data.get("photo3")) if data.get("photo3") else None
    photos.append(data.get("photo4")) if data.get("photo4") else None
    photos.append(data.get("photo5")) if data.get("photo5") else None
    photos.append(data.get("photo6")) if data.get("photo6") else None
    # summary = text(
    #     text(f"{html.underline('Job overview:\n')}"),
    #     text(f"{html.bold('Title:')} {title}\n"),
    #     text(f"{html.bold('Description:')} {html.italic(description)}\n"),
    #     text(f"{html.bold('Skills (required):')} {html.code(skills)}"),
    #     text(f"{html.blockquote(location)}"),
    # )
    summary = markdown.text(
                markdown.text(f'{description}\n'),
                markdown.hbold('Expected price: '),
                markdown.hitalic(f'{price}'),
                markdown.hblockquote(f'📍 {location}, {address}')
            )
    media = []
    for photo in photos:
        media.append(InputMediaPhoto(media=photo))
    media[-1].caption = summary
    await message.answer("New Living Post", reply_markup=ReplyKeyboardRemove())
    await message.answer_media_group(media=media)


# --- NEXT ---
@living_router.message(Livings.searching, F.text == "Next ➡️")
async def next_living(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # await state.set_state(Jobs.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        # job = await rq.get_next_job_by_id(session, user.jobs_search_id_list)
        living, photos = await search_funcitons_map[user.livings_city_search](session, user.livings_search_id_list, user.city)
        if living:
            summary = await living_summary(living, photos)
            await message.answer_media_group(media=summary)
            await rq.add_id_to_user_livings_search_id_list(session, user.user_id, living.id)
        elif living is None:
            if user.livings_city_search:
                await message.answer("No more livings options", reply_markup=ReplyKeyboardRemove())
                await message.answer("Would you like to search for livings outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
            else:
                await message.answer("No more livings posts", reply_markup=ReplyKeyboardRemove())
                await message.answer("You can come later to see new available livings options", reply_markup=nav.livingsChoiceMenu.as_markup())  
        else:
            await message.answer("No more livings posts", reply_markup=ReplyKeyboardRemove())
            await message.answer("You can come later to see new available livings options", reply_markup=nav.livingsChoiceMenu.as_markup()) 

# @living_router.message(Living.location, F.location)
# @living_router.message(Living.location, F.text)
# async def living_location(message: Message, state: FSMContext):
#     if message.location:
#         user_location = location.get_location(message.location.latitude, message.location.longitude)
#         print(user_location)
#         data = await state.update_data(location=user_location[1])
#     else:
#          data = await state.update_data(location=message.text)
#     await state.clear()

#     await show_summary(message=message, data=data)

#     await state.set_state(Livings.choice)
#     await message.answer("Good, your ad is successfully posted!", reply_markup=nav.livingsChoiceMenu)
#     await set_default_commands(id=message.from_user.id)

# async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
#     title = data["title"]
#     description = data["description"]
#     price = data["price"]
#     location = data["location"]
#     summary = text(
#         text(f"{html.underline('Ad overview:\n')}"),
#         text(f"{html.bold('Title:')} {title}\n"),
#         text(f"{html.bold('Description:')} {html.italic(description)}\n"),
#         text(f"{html.bold('Price:')} {html.code(price)}"),
#         text(f"{html.blockquote(location)}"),
#     )
#     await message.answer(text=summary, reply_markup=ReplyKeyboardRemove())

# @living_router.message()
# async def invalid_input(message: Message):
#      await message.answer("Please, provide a valid answer livings")


# --- HELPER FUNCTIONS ---
async def living_summary(living: Living, photos): # use ParseMode.HTML (parse_mode=ParseMode.HTML)
    summary = markdown.text(
                markdown.text(f'{living.description}\n'),
                markdown.hbold('Expected price: '),
                markdown.hitalic(f'{living.price}'),
                markdown.hbold(f'\nLandlord ->'),
                markdown.hlink(f'@{living.username}', f'https://t.me/{living.username}'),
                markdown.hblockquote(f'📍 {living.city}, {living.address}')
            )
    # summary = markdown.text(
    #             markdown.text(f'{description}\n'),
    #             markdown.hbold('Expected price: '),
    #             markdown.hitalic(f'{price}'),
    #             markdown.hblockquote(f'{location}, {address}')
    #         )
    media = []
    for photo in photos:
        media.append(InputMediaPhoto(media=photo.photo_id))
    media[-1].caption = summary
    return media


# --- ERROR HANDLING --- 
    # choice = State()
    # searching = State()

    # description = State()
    # photo1 = State()
    # photo2 = State()
    # photo3 = State()
    # photo4 = State()
    # photo5 = State()
    # photo6 = State()
    # price = State()
    # location = State()
    # # optional
    # address = State()
    
@living_router.message(Livings.choice)
async def choice_invalid(message: Message):
    await message.answer("I don't understand you. Please choose your action or Go /home")
@living_router.message(Livings.searching)
async def searching_invalid(message: Message):
    await message.answer("I don't understand you")
@living_router.message(Living.description)
async def description_invalid(message: Message):
    await message.answer("I don't understand you")
@living_router.message(Living.photo1)
@living_router.message(Living.photo2)
@living_router.message(Living.photo3)
@living_router.message(Living.photo4)
@living_router.message(Living.photo5)
@living_router.message(Living.photo6)
async def photos_invalid(message: Message):
    await message.answer("I don't understand you")
@living_router.message(Living.price)
async def price_invalid(message: Message):
    await message.answer("I don't understand you")
@living_router.message(Living.location)
async def location_invalid(message: Message):
    await message.answer("I don't understand you")
@living_router.message(Living.address)
async def address_invalid(message: Message):
    await message.answer("I don't understand you")

@living_router.callback_query(nav.MenuCallback.filter(F.menu == "my_livings"))
async def my_livings_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@living_router.callback_query(nav.MenuCallback.filter(F.menu == "post_living"))
async def post_living_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@living_router.callback_query(nav.MenuCallback.filter(F.menu == "livings_go_search_beyond"))
async def go_search_beyond_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
# END