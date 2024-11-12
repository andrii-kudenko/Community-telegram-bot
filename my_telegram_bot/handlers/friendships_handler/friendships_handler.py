# TO DO
# Handle search beyond city, think over the system how to differentiate whether the search is within city or beyond

from typing import Any, Dict
import logging
from sqlalchemy import BigInteger
from collections import defaultdict
import threading

from aiogram import Router, F, html
from aiogram.utils import markdown
from aiogram.utils.markdown import bold, italic, text, code, pre
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, BotCommand, CallbackQuery, InputMediaPhoto, InputFile, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from . import friendships_markup as nav
from utils import location
from bot_info import set_back_commands, set_default_commands, bot
from database import friends_requests as rq
from database.models import SessionLocal
from database.models import Bio as ProfileBio

friendship_router = Router(name=__name__)

class NewBio():
    def __init__(self, coordinates, user_id, profile_name, profile_bio, profile_age, city,
                 latitude = 0, longtitude = 0) -> None:
        self.coordinates = coordinates
        self.user_id = user_id
        self.profile_name = profile_name
        self.profile_bio = profile_bio
        self.profile_age = profile_age
        self.profile_city = city
        self.latitude = latitude
        self.longtitude = longtitude

class Friends(StatesGroup):
    choice = State()
    searching = State()
    bio_overview = State()

class Bio(StatesGroup):
    name = State()
    age = State()
    bio = State()
    photo1 = State()
    photo2 = State()
    photo3 = State()
    location = State()

# user_data = defaultdict(lambda: {'search_id': 0, 'my_bio_id': 0})
# lock = threading.Lock()

# ---UTILITY FUNCTIONS---
search_funcitons_map = { # execute appropriate function depending on the city_search value in bio
    True: rq.get_next_bio_by_id_with_city,
    False: rq.get_next_bio_by_id_without_city
}
update_funcitons_map = { # execute appropriate function depending on the city_search value in bio
    True: rq.update_my_search_id,
    False: rq.update_my_beyond_city_search_id
}
# def get_user_data(user_id: int):
#     with lock:
#         return user_data[user_id]
# def set_user_search_id(user_id: BigInteger, search_id: int):
#     with lock:
#         user_data[user_id]['search_id'] = search_id
#         return user_data[user_id]['search_id']
# def set_my_bio_id(user_id: BigInteger, bio_id: int):
#      with lock:
#         user_data[user_id]['my_bio_id'] = bio_id
#         return user_data[user_id]['my_bio_id']
# def get_my_bio_id(user_id: BigInteger):
#      with lock:
#         return user_data[user_id]['my_bio_id']
     

# --- COMMANDS ---
@friendship_router.message(Command("friends", prefix=("!/")))
async def start_friends(message: Message, state: FSMContext):    
    await message.answer("Hi there! Choose the action:", reply_markup=nav.friendsReplyChoiceMenu.as_markup())
@friendship_router.callback_query(nav.MenuCallback.filter(F.menu == "start_friends"))
async def start_friends_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    await query.answer("Friends")
    updated_keyboard = await nav.create_blank_keyboard("Friends 🤼")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    
    await query.message.answer("Hi there! Choose the action:", reply_markup=nav.friendsReplyChoiceMenu.as_markup())



@friendship_router.message(Bio.name, Command("cancel", prefix=("!/")))
@friendship_router.message(Bio.age, Command("cancel", prefix=("!/")))
@friendship_router.message(Bio.bio, Command("cancel", prefix=("!/")))
@friendship_router.message(Bio.photo1, Command("cancel", prefix=("!/")))
@friendship_router.message(Bio.photo2, Command("cancel", prefix=("!/")))
@friendship_router.message(Bio.photo3, Command("cancel", prefix=("!/")))
@friendship_router.message(Bio.location, Command("cancel", prefix=("!/")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.set_state(Friends.choice)
    await message.answer(
        "Cancelled. Choose the action:",
        reply_markup=nav.friendsReplyChoiceMenu.as_markup(),
    )
    await set_default_commands(id=message.from_user.id)
@friendship_router.message(Bio.name, Command("back", prefix=("!/")))
@friendship_router.message(Bio.age, Command("back", prefix=("!/")))
@friendship_router.message(Bio.bio, Command("back", prefix=("!/")))
@friendship_router.message(Bio.photo1, Command("back", prefix=("!/")))
@friendship_router.message(Bio.photo2, Command("back", prefix=("!/")))
@friendship_router.message(Bio.photo3, Command("back", prefix=("!/")))
@friendship_router.message(Bio.location, Command("back", prefix=("!/")))
async def back_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Bio.name:
            await state.set_state(Friends.choice)
            await message.answer("Hi there! Choose the action:", reply_markup=nav.friendsReplyChoiceMenu.as_markup())
    elif current_state == Bio.age:
            await state.set_state(Bio.name)
            await message.answer("Send me your name")
    elif current_state == Bio.bio:
            await state.set_state(Bio.age)
            await message.answer("Send me your age")
    elif current_state == Bio.photo1:
            await state.set_state(Bio.bio)
            await message.answer("Send me your bio")
    elif current_state == Bio.photo2:
            await state.set_state(Bio.photo1)
            await message.answer("Send me your photo")
    elif current_state == Bio.photo3:
            await state.set_state(Bio.photo2)
            await message.answer("Send me another photo")
    elif current_state == Bio.location:
            await state.set_state(Bio.photo3)
            await message.answer("Send me another photo")



# --- SEARCH ---
@friendship_router.callback_query(nav.FriendsCallback.filter(F.action == "search"))
async def search_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Searching")
    updated_keyboard = await nav.create_blank_keyboard("Search 🔎")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    async with SessionLocal() as session: # Check if my bio exists
        print(query.message.from_user.id)
        my_bio = await rq.get_my_bio_by_user_id_without_photos(session, user_id)
        print('My bio id:', my_bio.id, 'Search id:', my_bio.search_id)
        if my_bio:
            print("IN BIO")
            await rq.update_my_city_search(session, my_bio.id, True)
        else:
            print("NOT BIO")
            await query.answer("No Bio")
            await query.message.answer("You do not have a profile for this app. Let's create one")
            await new_bio_by_query(query, state)
            
    # await query.message.answer("Searching...", reply_markup=nav.likeMenu)
    await state.set_state(Friends.searching)
    async with SessionLocal() as session: # Get next bio
        my_bio = await rq.get_my_bio_by_user_id_without_photos(session, user_id)
        bio, photos = await rq.get_next_bio_by_id_with_city(session, my_bio.search_id, my_bio.id, my_bio.profile_city)
        if bio:
            await query.message.answer("Searching...", reply_markup=nav.likeMenu)
            print(bio.id, bio.profile_name)
            summary = markdown.text(
            markdown.hbold(f'{bio.profile_name}'),
            markdown.hunderline(f'{bio.profile_age} - '),
            markdown.hitalic(f'{bio.profile_bio}'),
            markdown.hblockquote(f'{bio.profile_city}')
            )
            media = []
            for photo in photos:
                media.append(InputMediaPhoto(media=photo.photo_id))
            media[-1].caption = summary
            await query.message.answer_media_group(media=media)
            updated = await rq.update_my_search_id(session, my_bio.id, bio.id)
            print('UPDATED', updated)
        elif bio is None:
            await query.message.answer("Searching...")
            await query.message.answer("No more profiles", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("Would you like to search beyond your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())
            return
        else:
            await query.message.answer("Searching...")
            await query.message.answer("No more profiles", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new users' profiles", reply_markup=nav.homeChoiceMenu.as_markup())

@friendship_router.callback_query(nav.FriendsCallback.filter(F.action == "search_beyond"))
async def search_beyond_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Searching beyond")
    updated_keyboard = await nav.create_blank_keyboard("Search beyond city 🔎")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    async with SessionLocal() as session: # Check if my bio exists
        print(query.message.from_user.id)
        my_bio = await rq.get_my_bio_by_user_id_without_photos(session, user_id)
        print('My bio id:', my_bio.id, 'Search id:', my_bio.search_id)
        if my_bio:
            print("IN BIO")
            await rq.update_my_city_search(session, my_bio.id, False)
        else:
            print("NOT BIO")
            await query.answer("No Bio")
            await query.message.answer("You do not have a profile for this app. Let's create one")
            await new_bio_by_query(query, state)
            
    # await query.message.answer("Searching...", reply_markup=nav.likeMenu)
    await state.set_state(Friends.searching)
    async with SessionLocal() as session: # Get next bio
        my_bio = await rq.get_my_bio_by_user_id_without_photos(session, user_id)
        bio, photos = await rq.get_next_bio_by_id_without_city(session, my_bio.beyond_city_search_id, my_bio.id, my_bio.profile_city)
        if bio:
            await query.message.answer("Searching...", reply_markup=nav.likeMenu)
            print(bio.id, bio.profile_name)
            summary = markdown.text(
            markdown.hbold(f'{bio.profile_name}'),
            markdown.hunderline(f'{bio.profile_age} - '),
            markdown.hitalic(f'{bio.profile_bio}'),
            markdown.hblockquote(f'{bio.profile_city}')
            )
            media = []
            for photo in photos:
                media.append(InputMediaPhoto(media=photo.photo_id))
            media[-1].caption = summary
            await query.message.answer_media_group(media=media)
            updated = await rq.update_my_beyond_city_search_id(session, my_bio.id, bio.id)
            print('UPDATED', updated)
        elif bio is None:
            await query.message.answer("Searching...")
            await query.message.answer("No more profiles", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new users' profiles", reply_markup=nav.homeChoiceMenu.as_markup())
        else:
            await query.message.answer("Searching...")
            await query.message.answer("No more profiles", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new users' profiles", reply_markup=nav.homeChoiceMenu.as_markup())


# --- MY BIO ---
@friendship_router.callback_query(nav.MenuCallback.filter(F.menu == "my_bio"))
async def my_bio_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("My Bio")
    await state.set_state(Friends.bio_overview)
    updated_keyboard = await nav.create_blank_keyboard("My Bio 👤")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    async with SessionLocal() as session:
        my_bio, photos = await rq.get_my_bio_by_user_id(session, user_id)
        if my_bio:
            summary = markdown.text(
                markdown.hbold(f'{my_bio.profile_name}'),
                markdown.hunderline(f'{my_bio.profile_age} - '),
                markdown.hitalic(f'{my_bio.profile_bio}'),
                markdown.hblockquote(f'{my_bio.profile_city}')
            )
            media = []
            if photos:
                for photo in photos:
                    media.append(InputMediaPhoto(media=photo.photo_id))
                media[-1].caption = summary
            last_message = await query.message.answer_media_group(media=media)
            # await query.message.a("My bio")
            await last_message[-1].answer(text="Choose action", reply_markup=nav.bioChangeMenu.as_markup())
            # await query.message.edit_text(text=summary, reply_markup=nav.bioChangeMenu.as_markup())
        else:
            await query.answer("No Bio")
            await query.message.edit_text("You do not have a profile for this app. Let's create one")
            await new_bio_by_query(query, state)

# --- NEW BIO ---
@friendship_router.callback_query(nav.FriendsCallback.filter(F.action == "new_bio"))
async def new_bio_by_query(query: CallbackQuery, state: FSMContext):
    await query.answer("Creating New Bio")
    updated_keyboard = await nav.create_blank_keyboard("New Bio 👤")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    await query.message.answer("Creating your profile...\
                         \nMind that you can always \nGo /back or /cancel the process")
    await state.set_state(Bio.name)
    await query.message.answer("Type your name:")
    await set_back_commands(id=query.from_user.id)

# --- BIO CREATION ---
@friendship_router.message(Bio.name, F.text)
async def profile_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Bio.age)
    await message.answer(f"Nice, {html.bold(message.text)}!\nNow, type your age:")
@friendship_router.message(Bio.age, F.text)
async def profile_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Bio.bio)
    await message.answer(f"Ok, now provide some information about you and your interests:")
@friendship_router.message(Bio.bio, F.text)
async def profile_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    await state.set_state(Bio.photo1)
    await message.answer(f"Cool! now provide a photo for your profile:")
@friendship_router.message(Bio.photo1, F.photo)
async def profile_photo1(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    new_photo = await state.update_data(photo1 = file_id)
    await state.set_state(Bio.photo2)
    await message.answer("Nice, you have uploaded one photo. Send another one or just continue with this one", reply_markup=nav.photosUploadingReplyMenu1)
@friendship_router.message(Bio.photo2, F.photo)
async def profile_photo2(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    new_photo = await state.update_data(photo2 = file_id)
    await state.set_state(Bio.photo3)
    await message.answer("Good, now you have 2 photos. Want to add one more?", reply_markup=nav.photosUploadingReplyMenu2)
@friendship_router.message(Bio.photo3, F.photo)
async def profile_photo3(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    new_photo = await state.update_data(photo3 = file_id)
    await state.set_state(Bio.location)
    await message.answer("Cool, now you have 3 photos for you profile", reply_markup=ReplyKeyboardRemove())
    await confirm_photos(message, state)
@friendship_router.message(Bio.photo2, F.text == "Continue with 1/3 photos")
@friendship_router.message(Bio.photo3, F.text == "Continue with 2/3 photos")
async def confirm_photos(message: Message, state: FSMContext):
    await state.set_state(Bio.location)
    await message.answer(f"Finally, provide your location:", reply_markup=nav.locationMenu)
@friendship_router.message(Bio.location, F.location)
@friendship_router.message(Bio.location, F.text)
async def profile_location(message: Message, state: FSMContext):
    if message.location:
        user_location = location.get_location(message.location.latitude, message.location.longitude)
        print(user_location)
        data = await state.update_data(location=user_location[1])
        print(data["location"])
        new_bio = NewBio(True, message.from_user.id, data["name"], data["bio"], data["age"], data["location"], message.location.latitude, message.location.longitude)
    else:
        city = message.text.strip().title()
        data = await state.update_data(location=city)
        new_bio = NewBio(False, message.from_user.id, data["name"], data["bio"], data["age"], message.text)
    await state.clear()
    await show_summary(message=message, data=data)
    async with SessionLocal() as session:  
        photos = []
        photos.append(data["photo1"])
        photos.append(data.get("photo2")) if data.get("photo2") else None
        photos.append(data.get("photo3")) if data.get("photo3") else None
        my_new_bio = await rq.add_bio_to_user_by_id(session, new_bio, photos)
        print("Bio added successfully")
    await state.set_state(Friends.choice)
    await message.answer("Cool, now go search for new connections!", reply_markup=nav.friendsReplyChoiceMenu.as_markup())
    await set_default_commands(id=message.from_user.id)


async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
    name = data["name"]
    bio = data["bio"]
    age = data["age"]
    location = data["location"]
    photos = []
    photos.append(data["photo1"])
    photos.append(data.get("photo2")) if data.get("photo2") else None
    photos.append(data.get("photo3")) if data.get("photo3") else None
    summary = markdown.text(
                markdown.hbold(f'{name}'),
                markdown.hunderline(f'{age} - '),
                markdown.hitalic(f'{bio}'),
                markdown.hblockquote(f'{location}')
            )
    media = []
    # media = [InputMediaPhoto(media=photos[0].photo_id)]
    for photo in photos:
        media.append(InputMediaPhoto(media=photo))
    media[-1].caption = summary
    await message.answer("Your Bio", reply_markup=ReplyKeyboardRemove())
    await message.answer_media_group(media=media)


# --- LIKE/DISLIKE ---
@friendship_router.message(Friends.searching, F.text == "👍")
async def searching_like(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with SessionLocal() as session: # Get my bio_id and my search_id
        my_bio = await rq.get_my_bio_by_user_id_without_photos(session, user_id)
        # await message.answer(f'Bio: {my_bio.id} Search: {my_bio.search_id}')
        print('My bio id:', my_bio.id, 'Search id:', my_bio.search_id)
    async with SessionLocal() as session: # Check for a match, with further functionalities
        print('IN MATCH My bio id:', my_bio.id, 'Search id:', my_bio.search_id)
        match = await rq.like_user(session, my_bio.id, my_bio.search_id)
        if match: # Send a message to the user that liked profile, and send a message to a user who was liked and matched
            await message.answer("It's a match!")
            matched_profile, matched_photos = await rq.get_bio_by_id(session, my_bio.search_id)
            matched_profile_info = await bot.get_chat(matched_profile.user_id)
            matched_profile_username = matched_profile_info.username
            my_profile, my_photos = await rq.get_bio_by_id(session, my_bio.id)
            my_profile_info = await bot.get_chat(my_profile.user_id)
            my_profile_username = my_profile_info.username
            profile = await profile_summary(matched_profile, matched_photos)
            await message.answer_media_group(media=profile)
            await message.answer(markdown.text(
                markdown.text('Go start conversation with 👉🏼'),
                markdown.hlink(f'{matched_profile.profile_name} 💬', f'https://t.me/{matched_profile_username}')
            ), link_preview_options=LinkPreviewOptions(is_disabled=True))
            await bot.send_message(matched_profile.user_id, markdown.text(
                markdown.text("You've got a match ❤️‍🔥\n"),
                markdown.text("\bGo start conversation with 👉🏼"),
                markdown.hlink(f'{my_profile.profile_name} 💬', f'https://t.me/{my_profile_username}')
            ), link_preview_options=LinkPreviewOptions(is_disabled=True))
    async with SessionLocal() as session: # Update search_id, continue with next bio
        print('IN SEARCH My bio id:', my_bio.id, 'Search id:', my_bio.search_id)
        target_search_id = my_bio.search_id if my_bio.city_search else my_bio.beyond_city_search_id
        bio, photos = await search_funcitons_map[my_bio.city_search](session, target_search_id, my_bio.id, my_bio.profile_city)
        print('IN SEARCH My bio id:', my_bio.id, 'Search id:', my_bio.search_id)
        if bio: # make inputs for photos
            print(bio.id, bio.profile_name)
            summary = markdown.text(
            markdown.hbold(f'{bio.profile_name}'),
            markdown.hunderline(f'{bio.profile_age} - '),
            markdown.hitalic(f'{bio.profile_bio}'),
            markdown.hblockquote(f'{bio.profile_city}')
            )
            media = []
            for photo in photos:
                media.append(InputMediaPhoto(media=photo.photo_id))
            media[-1].caption = summary
            await message.answer_media_group(media=media)
            updated = await update_funcitons_map[my_bio.city_search](session, my_bio.id, bio.id)
            print('UPDATED', updated)
        elif bio is None:
            if my_bio.city_search:
                await message.answer("No more profiles", reply_markup=ReplyKeyboardRemove())
                await message.answer("Would you like to search beyond your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())
            else:
                await message.answer("Cool, that's it. You've viewed all available profiles 👏", reply_markup=ReplyKeyboardRemove())
                await message.answer("Now you can chill and wait until someone finds your profile interesting", reply_markup=nav.homeChoiceMenu.as_markup())
        else:
             await message.answer("Cool, that's it. You've viewed all available profiles 👏", reply_markup=ReplyKeyboardRemove())
             await message.answer("Now you can chill and wait until someone finds your profile interesting", reply_markup=nav.homeChoiceMenu.as_markup())
@friendship_router.message(Friends.searching, F.text == "👎")
async def searching_dislike(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with SessionLocal() as session: # Get my bio_id and my search_id
        my_bio = await rq.get_my_bio_by_user_id_without_photos(session, user_id)
        print('My bio id:', my_bio.id, 'Search id:', my_bio.search_id)
    async with SessionLocal() as session: # Update search_id, continue with next bio
        target_search_id = my_bio.search_id if my_bio.city_search else my_bio.beyond_city_search_id
        bio, photos = await search_funcitons_map[my_bio.city_search](session, target_search_id, my_bio.id, my_bio.profile_city)
        if bio:
            print(bio.id, bio.profile_name)
            summary = markdown.text(
            markdown.hbold(f'{bio.profile_name}'),
            markdown.hunderline(f'{bio.profile_age} - '),
            markdown.hitalic(f'{bio.profile_bio}'),
            markdown.hblockquote(f'{bio.profile_city}')
            )
            media = []
            for photo in photos:
                media.append(InputMediaPhoto(media=photo.photo_id))
            media[-1].caption = summary
            await message.answer_media_group(media=media)
            updated = await update_funcitons_map[my_bio.city_search](session, my_bio.id, bio.id)
            print('UPDATED', updated)
        elif bio is None:
            if my_bio.city_search:
                await message.answer("No more profiles", reply_markup=ReplyKeyboardRemove())
                await message.answer("Would you like to search beyond your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())
            else:
                await message.answer("Cool, that's it. You've viewed all available profiles 👏", reply_markup=ReplyKeyboardRemove())
                await message.answer("Now you can chill and wait until someone finds your profile interesting", reply_markup=nav.homeChoiceMenu.as_markup())
        else:
             await message.answer("Cool, that's it. You've viewed all available profiles 👏", reply_markup=ReplyKeyboardRemove())
             await message.answer("Now you can chill and wait until someone finds your profile interesting", reply_markup=nav.homeChoiceMenu.as_markup())


# --- HELPER FUNCTIONS ---
async def profile_summary(bio, photos):
    summary = markdown.text(
            markdown.hbold(f'{bio.profile_name}'),
            markdown.hunderline(f'{bio.profile_age} - '),
            markdown.hitalic(f'{bio.profile_bio}'),
            markdown.hblockquote(f'{bio.profile_city}')
            )
    media = []
    # media = [InputMediaPhoto(media=photos[0].photo_id)]
    for photo in photos:
        media.append(InputMediaPhoto(media=photo.photo_id))
    media[-1].caption = summary
    return media



# --- ERROR HANDLING --- 
    # choice = State()
    # searching = State()
    # bio_overview = State()
    
    # name = State()
    # age = State()
    # bio = State()
    # photo1 = State()
    # photo2 = State()
    # photo3 = State()
    # location = State()
    
@friendship_router.message(Friends.choice)
async def choice_invalid(message: Message):
    await message.answer("I don't understand you. Please choose your action or Go /home")
@friendship_router.message(Friends.searching)
async def searching_invalid(message: Message):
    await message.answer("I don't understand you")
@friendship_router.message(Friends.bio_overview)
async def bio_overview_invalid(message: Message):
    await message.answer("I don't understand you")
@friendship_router.message(Bio.name)
async def name_invalid(message: Message):
    await message.answer("I don't understand you")
@friendship_router.message(Bio.age)
async def age_invalid(message: Message):
    await message.answer("I don't understand you")
@friendship_router.message(Bio.bio)
async def bio_invalid(message: Message):
    await message.answer("I don't understand you")
@friendship_router.message(Bio.photo1)
@friendship_router.message(Bio.photo2)
@friendship_router.message(Bio.photo3)
async def photo1_invalid(message: Message):
    await message.answer("I don't understand you")
@friendship_router.message(Bio.location)
async def location_invalid(message: Message):
    await message.answer("I don't understand you")

@friendship_router.callback_query(nav.MenuCallback.filter(F.menu == "my_bio"))
async def my_bio_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@friendship_router.callback_query(nav.MenuCallback.filter(F.menu == "new_bio"))
async def new_bio_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@friendship_router.callback_query(nav.MenuCallback.filter(F.menu == "friendships_go_search"))
async def go_search_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@friendship_router.callback_query(nav.MenuCallback.filter(F.menu == "friendships_go_search_beyond"))
async def go_search_beyond_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
# END