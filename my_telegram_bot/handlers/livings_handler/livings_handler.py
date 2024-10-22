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
from database.models import SessionLocal, Living as LivingModel

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
class LivingEdit(StatesGroup):
    living_id = State()
    photo_id = State()
    description = State()
    new_photo = State()
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
    await message.answer("Hi there! Choose the action:", reply_markup=nav.livingsReplyChoiceMenu.as_markup())
@living_router.callback_query(nav.MenuCallback.filter(F.menu == "start_livings"))
@living_router.callback_query(nav.LivingsCallback.filter(F.action == "start_livings"))
async def start_livings_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext): # HAS Middleware
    # ...
    if "action" in callback_data.model_dump():
        await query.answer("Livings")
        updated_keyboard = await nav.create_blank_keyboard(f"{callback_data.additional}")
        await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    await query.message.answer("Hi there! Choose the action:", reply_markup=nav.livingsReplyChoiceMenu.as_markup())


@living_router.message(Living.description, Command("cancel", prefix=("!/")))
@living_router.message(Living.photo1, Command("cancel", prefix=("!/")))
@living_router.message(Living.photo2, Command("cancel", prefix=("!/")))
@living_router.message(Living.photo3, Command("cancel", prefix=("!/")))
@living_router.message(Living.photo4, Command("cancel", prefix=("!/")))
@living_router.message(Living.photo5, Command("cancel", prefix=("!/")))
@living_router.message(Living.photo6, Command("cancel", prefix=("!/")))
@living_router.message(Living.price, Command("cancel", prefix=("!/")))
@living_router.message(Living.location, Command("cancel", prefix=("!/")))
@living_router.message(Living.address, Command("cancel", prefix=("!/")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.set_state(Livings.choice)
    await message.answer(
        "Cancelled",
        reply_markup=nav.livingsChoiceMenu.as_markup(),
    )
    await set_default_commands(id=message.from_user.id)

@living_router.message(Living.description, Command("back", prefix=("!/")))
@living_router.message(Living.price, Command("back", prefix=("!/")))
@living_router.message(Living.location, Command("back", prefix=("!/")))
@living_router.message(Living.photo1, Command("back", prefix=("!/")))
@living_router.message(Living.photo2, Command("back", prefix=("!/")))
@living_router.message(Living.photo3, Command("back", prefix=("!/")))
@living_router.message(Living.photo4, Command("back", prefix=("!/")))
@living_router.message(Living.photo5, Command("back", prefix=("!/")))
@living_router.message(Living.photo6, Command("back", prefix=("!/")))
async def back_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Living.description:
        await state.set_state(Livings.choice)
        await message.answer("Choose action:", reply_markup=nav.livingsReplyChoiceMenu.as_markup())
    elif current_state == Living.photo1:
        await state.set_state(Living.description)
        await message.answer("Send me new description")
    elif current_state == Living.photo2:
        await state.set_state(Living.photo1)
        await message.answer("Send me another photo")
    elif current_state == Living.photo3:
        await state.set_state(Living.photo2)
        await message.answer("Send me another photo")
    elif current_state == Living.photo4:
        await state.set_state(Living.photo3)
        await message.answer("Send me another photo")
    elif current_state == Living.photo5:
        await state.set_state(Living.photo4)
        await message.answer("Send me another photo")
    elif current_state == Living.photo6:
        await state.set_state(Living.photo5)
        await message.answer("Send me another photo")
    elif current_state == Living.price:
        await state.set_state(Living.photo6)
        await message.answer("Send me another photo")
    elif current_state == Living.location:
        await state.set_state(Living.price)
        await message.answer("Send me new price")
    elif current_state == Living.address:
        await state.set_state(Living.location)
        await message.answer("Send me new location")
    else:
        pass



# --- SEARCH ---
@living_router.callback_query(nav.LivingsCallback.filter(F.action == "search"))
async def search_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Searching")
    updated_keyboard = await nav.create_blank_keyboard("Search 🔎")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)  
    # database call
    async with SessionLocal() as session:
        await rq.update_my_livings_city_search(session, user_id, True)
    # await query.message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Livings.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        living, photos = await rq.get_next_living_with_city(session, user.livings_search_id_list, user.city)
        if living:
            await query.message.answer("Searching...", reply_markup=nav.nextMenu)
            summary = await living_summary(living, photos)
            await query.message.answer_media_group(media=summary)
            await rq.add_id_to_user_livings_search_id_list(session, user.user_id, living.id)
            # updated = await rq.add_id_to_user_sales_jobs_search_id_list()
        elif living is None:
            await query.message.answer("Searching...")
            await query.message.answer("No more livings options", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("Would you like to search for livings outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())
        else:
            await query.message.answer("Searching...")
            await query.message.answer("No more livings posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available livings options", reply_markup=nav.livingsChoiceMenu.as_markup())
@living_router.callback_query(nav.LivingsCallback.filter(F.action == "search_beyond"))
async def search_beyond_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Searching beyond")
    updated_keyboard = await nav.create_blank_keyboard("Search beyond city 🔎")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    async with SessionLocal() as session:
        await rq.update_my_livings_city_search(session, user_id, False)
    # await query.message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Livings.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        living, photos = await rq.get_next_living_without_city(session, user.livings_search_id_list, user.city)
        if living:
            await query.message.answer("Searching...", reply_markup=nav.nextMenu)
            summary = await living_summary(living, photos)
            await query.message.answer_media_group(media=summary)
            await rq.add_id_to_user_livings_search_id_list(session, user.user_id, living.id)
        elif living is None:
            await query.message.answer("Searching...")
            await query.message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available sales options", reply_markup=nav.livingsChoiceMenu.as_markup()) 
        elif living is None:
            await query.message.answer("Searching...")
            await query.message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available sales options", reply_markup=nav.livingsChoiceMenu.as_markup()) 


# --- NEW LIVING ---
@living_router.callback_query(nav.LivingsCallback.filter(F.action == "post_ad"))
async def new_living_by_query(query: CallbackQuery, state: FSMContext):
    await query.answer("Creating New Post")
    updated_keyboard = await nav.create_blank_keyboard("Post an ad 📰")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    await query.message.answer("Creating your ad...\
                         \nMind that you can always \nGo /back or /cancel the process")
    await state.set_state(Living.description)
    await query.message.answer("Provide a full description for your ad:")
    await set_back_commands(id=query.from_user.id)


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
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.livingsReplyChoiceMenu.as_markup())
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
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.livingsReplyChoiceMenu.as_markup())

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


# --- MY POSTS ---
@living_router.callback_query(nav.MenuCallback.filter(F.menu == "my_livings"))
@living_router.callback_query(nav.LivingsCallback.filter(F.action == "my_livings"))
async def my_livings_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("My Ads")
    if "menu" in callback_data.model_dump():
        updated_keyboard = await nav.create_blank_keyboard("View my living ads 🧾")
    elif "action" in callback_data.model_dump():
        updated_keyboard = await nav.create_blank_keyboard(callback_data.additional)
    else:
        updated_keyboard = await nav.create_blank_keyboard("Deleted")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    # make a database request
    # and further manipulations
    async with SessionLocal() as session:     
        my_livings = await rq.get_user_livings(session, user_id)   
        for living in my_livings:
            print(living.description)
        if my_livings:
            keyboard = await nav.create_livings_keyboard(my_livings)
            await query.message.answer("My Living Ads", reply_markup=keyboard)
        else:
            answer = await query.message.answer("You have no livings ads")
            await start_livings(answer, state)

@living_router.callback_query(nav.LivingsCallback.filter(F.action == "manage"))
async def handle_single_item_list_by_query(query: CallbackQuery, callback_data: nav.LivingsCallback, state: FSMContext):
    await query.answer("Living")
    living_id, additional = int(callback_data.id), callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard(f"{additional}")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    # await query.message.answer(query.chat_instance)
    # Query the job
    async with SessionLocal() as session:
        my_living, photos = await rq.get_living_by_id(session, living_id)
        if my_living:
            keyboard = await nav.create_single_living_keyboard(my_living.id, my_living.description, photos)
            summary = await living_summary(my_living, photos)
            await query.message.answer_media_group(media=summary)
            await query.message.answer(text="Actions for the above 🔝 living", reply_markup=keyboard) 
        else:
            await query.message.answer("You do not have any posts")
async def handle_single_item_list_by_message(message: Message, callback_data: nav.LivingsCallback, state: FSMContext):
    item_id, additional = int(callback_data.id), callback_data.additional
    async with SessionLocal() as session:
        my_living, photos = await rq.get_living_by_id(session, item_id)
        if my_living:
            keyboard = await nav.create_single_living_keyboard(my_living.id, my_living.description, photos)
            summary = await living_summary(my_living, photos)
            await message.answer_media_group(media=summary)
            await message.answer(text="Actions for the above 🔝 living", reply_markup=keyboard) 
        else:
            await message.answer("You do not have any posts")

@living_router.callback_query(nav.LivingsCallback.filter(F.action == "delete"))
async def handle_item_delete_by_query(query: CallbackQuery, callback_data: nav.LivingsCallback, state: FSMContext):
    my_living = int(callback_data.id)
    additional = callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard(f"{additional}")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    print("ID", my_living)
    # Delete the item
    async with SessionLocal() as session:
        deleted_living = await rq.delete_living_by_id(session, my_living)
        if deleted_living:
            await query.answer("Deleted")
            # await query.message.answer("Job post successfully deleted")
            # await query.message.edit_reply_markup(ReplyKeyboardRemove())
            callback_data = nav.BlankCallback(text="Deleted")
            await my_livings_by_query(query, callback_data, state)
        else:
            await query.answer("Error")
            callback_data = nav.BlankCallback(text="Error")
            await my_livings_by_query(query, callback_data, state)


@living_router.callback_query(nav.LivingsCallback.filter(F.action == "edit"))
async def handle_item_edit_by_query(query: CallbackQuery, callback_data: nav.LivingsCallback, state: FSMContext):
    await query.answer("Edit")
    living_id = int(callback_data.id)
    photos_string = callback_data.additional
    # additional = callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard("✏️ Edit")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    keyboard = await nav.create_edit_living_keyboard(living_id, photos_string)
    await query.message.answer("What do you want to edit?", reply_markup=keyboard)
@living_router.callback_query(nav.LivingsCallback.filter())
async def handle_item_field_edit_by_query(query: CallbackQuery, callback_data: nav.LivingsCallback, state: FSMContext):
    item_id = int(callback_data.id)
    await state.set_state(LivingEdit.living_id)
    await state.update_data(item_id=item_id)
    photo_id = int(callback_data.additional)
    await state.set_state(LivingEdit.photo_id)
    await state.update_data(photo_id=photo_id)
    await query.answer(f"{callback_data.action.capitalize()}")
    match callback_data.action:
        case "description":
            updated_keyboard = await nav.create_blank_keyboard("description")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(Living.description)
            await query.message.answer("Provide new description")
        case "price":
            updated_keyboard = await nav.create_blank_keyboard("price")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(Living.price)
            await query.message.answer("Provide new price")
        case "city":
            updated_keyboard = await nav.create_blank_keyboard("city")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(Living.location)
            await query.message.answer("Provide new location")
        case "address":
            updated_keyboard = await nav.create_blank_keyboard("location")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(Living.address)
            await query.message.answer("Provide new location")
        case "photo_1" | "photo_2" | "photo_3" | "photo_4" | "photo_5" | "photo_6":
            photo_splitted = callback_data.action.split("_")
            text = (" ").join(photo_splitted)
            updated_keyboard = await nav.create_blank_keyboard(text)
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(LivingEdit.new_photo)
            await query.message.answer("Provide new photo")


@living_router.message(LivingEdit.description, F.text)
@living_router.message(LivingEdit.price, F.text)
@living_router.message(LivingEdit.location, F.location)
@living_router.message(LivingEdit.location, F.text)
@living_router.message(LivingEdit.new_photo, F.photo)
async def handle_item_field_update_callback(message: Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    item_id = data["item_id"]
    photo_id = data["photo_id"]
    callback_data = nav.LivingsCallback(id=str(item_id), action="list", additional="")
    match current_state:
        # case LivingEdit.title.state:
        #     print("ITEM ID", item_id)
        #     print("Current State", current_state)
        #     # DB query to edit field
        #     async with SessionLocal() as session:
        #         updated = await rq.update_item_by_id(session, item_id, Item.title, message.text) 
        #         if updated:
        #             await message.answer("Title successfully updated")
        #             await handle_single_item_list_by_message(message, callback_data, state)
        #         else: 
        #             await message.answer("Error")
        case LivingEdit.description.state:
            async with SessionLocal() as session:
                updated = await rq.update_living_by_id(session, item_id, LivingModel.description, message.text) 
                if updated:
                    await message.answer("Description successfully updated")
                    await handle_single_item_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case LivingEdit.price.state:
            async with SessionLocal() as session:
                updated = await rq.update_living_by_id(session, item_id, LivingModel.price, message.text) 
                if updated:
                    await message.answer("Price successfully updated")
                    await handle_single_item_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case LivingEdit.location.state:
            if message.location:
                user_location = location.get_location(message.location.latitude, message.location.longitude)
                print(user_location)
                address = user_location[1]
                async with SessionLocal() as session:
                    updated = await rq.update_living_by_id(session, item_id, LivingModel.city, address)
                    if updated:
                        await message.answer("Location successfully updated")
                        await handle_single_item_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
            else:
                async with SessionLocal() as session:
                    updated = await rq.update_living_by_id(session, item_id, LivingModel.city, message.text) 
                    if updated:
                        await message.answer("City successfully updated")
                        await handle_single_item_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
        case LivingEdit.address.state:
            async with SessionLocal() as session:
                updated = await rq.update_living_by_id(session, item_id, LivingModel.price, message.text) 
                if updated:
                    await message.answer("Price successfully updated")
                    await handle_single_item_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case LivingEdit.new_photo.state:
            if message.photo:
                file_id = message.photo[-1].file_id
                async with SessionLocal() as session:
                    print("PHOTO", photo_id, "FILE_ID", file_id)
                    updated = await rq.update_living_photo_by_id(session, photo_id, file_id)
                    if updated:
                        await message.answer("Photo successfully updated")
                        await handle_single_item_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
            else:
                await message.answer("Provide a photo")                   



# --- HELPER FUNCTIONS ---
async def living_summary(living: Living, photos): # use ParseMode.HTML (parse_mode=ParseMode.HTML)
    summary = markdown.text(
                markdown.text(f'{living.description}'),
                markdown.hbold('\nExpected price:'),
                markdown.hitalic(f'{living.price}'),
                markdown.hbold(f'\nLandlord ⇾'),
                markdown.hlink(f'@{living.username}', f'https://t.me/{living.username}'),
                markdown.hblockquote(f'📍 {living.city}, {living.address}')
            )
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