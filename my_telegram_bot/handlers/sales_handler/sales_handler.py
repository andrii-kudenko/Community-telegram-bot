from typing import Any, Dict
import logging

from aiogram import Router, F, html
from aiogram.utils import markdown
from aiogram.utils.markdown import bold, italic, text, code, pre
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, InputMediaPhoto, FSInputFile, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData

from . import sales_markup as nav
from utils import location
from bot_info import set_back_commands, set_default_commands
from database import sales_requests as rq
from database.models import SessionLocal
from database.models import SaleItem as SaleItemModel

sales_router = Router(name=__name__)

class NewSaleItem():
    def __init__(self, user_id, username, title, description, price, city) -> None:
        self.user_id = user_id
        self.username = username
        self.title = title
        self.description = description
        self.price = price
        self.city = city

class Sales(StatesGroup):
    choice = State()
    searching = State()

class SaleItem(StatesGroup):
    title = State()
    description = State()
    photo1 = State()
    photo2 = State()
    photo3 = State()
    price = State()
    location = State()
class SaleItemEdit(StatesGroup):
    item_id = State()
    photo_id = State()
    title = State()
    description = State()
    photo1 = State()
    photo2 = State()
    photo3 = State()
    price = State()
    location = State()

# ---UTILITY FUNCTIONS---
search_funcitons_map = { # execute appropriate function depending on the city_search value in bio
    True: rq.get_next_item_with_city,
    False: rq.get_next_item_without_city
}


# --- COMMANDS ---
@sales_router.message(Command("sales", prefix=("!/")))
async def start_sales(message: Message, state: FSMContext):
    await message.answer("Hi there! Choose the action:", reply_markup=nav.salesReplyChoiceMenu.as_markup())
@sales_router.callback_query(nav.MenuCallback.filter(F.menu == "start_sales"))
@sales_router.callback_query(nav.SalesCallback.filter(F.action == "start_sales"))
async def start_sales_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext): # HAS Middleware
    # ...
    if "action" in callback_data.model_dump():
        await query.answer("Sales")
        updated_keyboard = await nav.create_blank_keyboard(f"{callback_data.additional}")
        await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    # await query.answer("Sales")
    # updated_keyboard = await nav.create_blank_keyboard("Sales 💵")
    # await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    await query.message.answer("Hi there! Choose the action:", reply_markup=nav.salesReplyChoiceMenu.as_markup())


@sales_router.message(SaleItem.title, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.description, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.price, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.location, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.photo1, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.photo2, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.photo3, Command("cancel", prefix=("!/")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.set_state(Sales.choice)
    await message.answer(
        "Cancelled",
        reply_markup=nav.salesChoiceMenu.as_markup(),
    )
    await set_default_commands(id=message.from_user.id)

@sales_router.message(SaleItem.title, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.description, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.photo1, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.photo2, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.photo3, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.price, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.location, Command("back", prefix=("!/")))
async def back_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == SaleItem.title:
            await state.set_state(Sales.choice)
            await message.answer("Choose action:", reply_markup=nav.salesChoiceMenu.as_markup())
    elif current_state == SaleItem.description:
            await state.set_state(SaleItem.title)
            await message.answer("Send me new title")
    elif current_state == SaleItem.photo1:
            await state.set_state(SaleItem.description)
            await message.answer("Send me new description")
    elif current_state == SaleItem.photo2:
            await state.set_state(SaleItem.photo1)
            await message.answer("Send me another photo")
    elif current_state == SaleItem.photo3:
            await state.set_state(SaleItem.photo2)
            await message.answer("Send me another photo")
    elif current_state == SaleItem.price:
            await state.set_state(SaleItem.photo3)
            await message.answer("Send me another photo")
    elif current_state == SaleItem.location:
            await state.set_state(SaleItem.price)
            await message.answer("Send me new price")
    else:
         pass



# --- SEARCH ---
@sales_router.callback_query(nav.SalesCallback.filter(F.action == "search"))
async def search_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Searching")
    updated_keyboard = await nav.create_blank_keyboard("Search 🔎")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)  
    # database call
    async with SessionLocal() as session:
        await rq.update_my_sales_city_search(session, user_id, True)
    # await query.message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Sales.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        item, photos = await rq.get_next_item_with_city(session, user.items_search_id_list, user.city)
        if item:
            await query.message.answer("Searching...", reply_markup=nav.nextMenu)
            summary = await item_summary(item, photos)
            await query.message.answer_media_group(media=summary)
            await rq.add_id_to_user_items_search_id_list(session, user.user_id, item.id)
            # updated = await rq.add_id_to_user_sales_jobs_search_id_list()
        elif item is None:
            await query.message.answer("Searching...")
            await query.message.answer("No more sales options", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("Would you like to search for sales options outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())
        else:
            await query.message.answer("Searching...")
            await query.message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available sales options", reply_markup=nav.salesChoiceMenu.as_markup())  
@sales_router.callback_query(nav.SalesCallback.filter(F.action == "search_beyond"))
async def search_beyond_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Searching beyond")
    updated_keyboard = await nav.create_blank_keyboard("Search beyond city 🔎")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    async with SessionLocal() as session:
        await rq.update_my_sales_city_search(session, user_id, False)
    # await query.message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Sales.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        item, photos = await rq.get_next_item_without_city(session, user.jobs_search_id_list, user.city)
        if item:
            await query.message.answer("Searching...", reply_markup=nav.nextMenu)
            summary = await item_summary(item, photos)
            await query.message.answer_media_group(media=summary)
            await rq.add_id_to_user_items_search_id_list(session, user.user_id, item.id)
        elif item is None:
            await query.message.answer("Searching...")
            await query.message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available sales options", reply_markup=nav.salesChoiceMenu.as_markup())  
        else:
            await query.message.answer("Searching...")
            await query.message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available sales options", reply_markup=nav.salesChoiceMenu.as_markup())  







# --- NEW ITEM ---
@sales_router.callback_query(nav.SalesCallback.filter(F.action == "post_item"))
async def new_item_by_query(query: CallbackQuery, state: FSMContext):
    await query.answer("Creating New Post")
    updated_keyboard = await nav.create_blank_keyboard("Post item 📰")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    await query.message.answer("Creating your ad...\
                         \nMind that you can always \nGo /back or /cancel the process")                   
    await state.set_state(SaleItem.title)
    await query.message.answer("Type the title for your ad:")
    await set_back_commands(id=query.from_user.id)



# --- ITEM CREATION ---
@sales_router.message(SaleItem.title, F.text)
async def ad_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(SaleItem.description)
    await message.answer(f"Now, provide some description:")
# @sales_router.message(SaleItem.description, F.text)
# async def ad_description(message: Message, state: FSMContext):
#     await state.update_data(description=message.text)
#     await state.set_state(SaleItem.price)
#     await message.answer(f"Ok, now set the price for your ad:")
@sales_router.message(SaleItem.description, F.text)
async def ad_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(SaleItem.photo1)
    await message.answer(f"Ok, now provide the first photo for your ad:")
@sales_router.message(SaleItem.photo1, F.photo)
async def ad_photo1(message: Message, state: FSMContext):
     file_id = message.photo[-1].file_id
     await state.update_data(photo1 = file_id)
     await state.set_state(SaleItem.photo2)
     await message.answer("Nice, you have uploaded one photo. Send another one or just continue with this one", reply_markup=nav.photosUploadingReplyMenu1)
@sales_router.message(SaleItem.photo2, F.photo)
async def ad_photo2(message: Message, state: FSMContext):
     file_id = message.photo[-1].file_id
     await state.update_data(photo2 = file_id)
     await state.set_state(SaleItem.photo3)
     await message.answer("Good, now you have 2 photos. Want to add one more?", reply_markup=nav.photosUploadingReplyMenu2)
@sales_router.message(SaleItem.photo3, F.photo)
async def ad_photo3(message: Message, state: FSMContext):
     file_id = message.photo[-1].file_id
     await state.update_data(photo3 = file_id)
     await state.set_state(SaleItem.location)
     await message.answer("Cool, now you have 3 photos for you ad", reply_markup=ReplyKeyboardRemove())
     await confirm_photos(message, state)
@sales_router.message(SaleItem.photo2, F.text == "Continue with 1/3 photos")
@sales_router.message(SaleItem.photo3, F.text == "Continue with 2/3 photos")
async def confirm_photos(message: Message, state: FSMContext):
    await state.set_state(SaleItem.price)
    await message.answer(f"Now, provide price for the item:", reply_markup=ReplyKeyboardRemove())
@sales_router.message(SaleItem.price, F.text)
async def ad_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(SaleItem.location)
    await message.answer(f"Ok, now give the location for your ad:", reply_markup=nav.locationMenu)
@sales_router.message(SaleItem.location, F.location)
@sales_router.message(SaleItem.location, F.text)
async def ad_location(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    if message.location:
        user_location = location.get_location(message.location.latitude, message.location.longitude)
        print(user_location)
        data = await state.update_data(location=user_location[1])
        new_item = NewSaleItem(user_id, username, data["title"], data["description"], data["price"], data["location"])
    else:
        data = await state.update_data(location=message.text)
        new_item = NewSaleItem(user_id, username, data["title"], data["description"], data["price"], data["location"])
    await state.clear()

    await show_summary(message=message, data=data)
    # database call to add
    async with SessionLocal() as session:
        photos = []
        photos.append(data["photo1"])
        photos.append(data.get("photo2")) if data.get("photo2") else None
        photos.append(data.get("photo3")) if data.get("photo3") else None
        new_sale_item = await rq.add_item_to_user_by_id(session, new_item, photos)
        print("Sale item created successfully")

    await state.set_state(Sales.choice)
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.salesReplyChoiceMenu.as_markup())
    await set_default_commands(id=message.from_user.id)
async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
    title = data["title"]
    description = data["description"]
    price = data["price"]
    location = data["location"]
    photos = []
    photos.append(data["photo1"])
    photos.append(data.get("photo2")) if data.get("photo2") else None
    photos.append(data.get("photo3")) if data.get("photo3") else None
    # summary = text(
    #     text(f"{html.bold('Title:')} {title}\n"),
    #     text(f"{html.bold('Description:')} {html.italic(description)}\n"),
    #     text(f"{html.bold('Price:')} {html.code(price)}"),
    #     text(f"{html.blockquote(location)}"),
    # )
    summary = markdown.text(
                markdown.hbold(f'{title} |'),
                markdown.hunderline(f'{price}\n'),
                markdown.hitalic(f'{description}'),
                markdown.hblockquote(f'{location}')
            )
    media = []
    for photo in photos:
         media.append(InputMediaPhoto(media=photo))
    media[-1].caption = summary
    await message.answer("New Sale Item", reply_markup=ReplyKeyboardRemove())
    await message.answer_media_group(media=media)




# --- NEXT ---
@sales_router.message(Sales.searching, F.text == "Next ➡️")
async def next_job(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # await state.set_state(Jobs.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        # job = await rq.get_next_job_by_id(session, user.jobs_search_id_list)
        item, photos = await search_funcitons_map[user.items_city_search](session, user.items_search_id_list, user.city)
        if item:
            summary = await item_summary(item, photos)
            await message.answer_media_group(media=summary)
            await rq.add_id_to_user_items_search_id_list(session, user.user_id, item.id)
        elif item is None:
            if user.items_city_search:
                await message.answer("No more item posts", reply_markup=ReplyKeyboardRemove())
                await message.answer("Would you like to search for sales options outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
            else:
                await message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
                await message.answer("You can come later to see new available sales options", reply_markup=nav.salesChoiceMenu.as_markup())  
        else:
            await message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
            await message.answer("You can come later to see new available sales options", reply_markup=nav.salesChoiceMenu.as_markup())  



# --- MY POSTS ---
@sales_router.callback_query(nav.MenuCallback.filter(F.menu == "my_items"))
@sales_router.callback_query(nav.SalesCallback.filter(F.action == "my_items"))
async def my_items_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("My Ads")
    if "menu" in callback_data.model_dump(): 
        updated_keyboard = await nav.create_blank_keyboard("View my sale ads🧾")
    elif "action" in callback_data.model_dump():
        updated_keyboard = await nav.create_blank_keyboard("Back")
    else:
        updated_keyboard = await nav.create_blank_keyboard("Deleted")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    # make a database request
    # and further manipulations
    async with SessionLocal() as session:
        my_items = await rq.get_user_items(session, user_id)
        for item in my_items:
            print(item.title, item.price)
        if my_items:
            keyboard = await nav.create_items_keyboard(my_items)
            await query.message.answer("My sales ads", reply_markup=keyboard)
        else:
            answer = await query.message.answer("You have no sales ads")
            await start_sales(answer, state)

@sales_router.callback_query(nav.SalesCallback.filter(F.action == "manage"))
async def handle_single_item_list_by_query(query: CallbackQuery, callback_data: nav.SalesCallback, state: FSMContext):
    await query.answer("Item")
    item_id, additional = int(callback_data.id), callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard(f"{additional}")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    # await query.message.answer(query.chat_instance)
    # Query the job
    async with SessionLocal() as session:
        my_item, photos = await rq.get_item_by_id(session, item_id)
        if my_item:
            keyboard = await nav.create_single_item_keyboard(my_item.id, my_item.title, photos)
            summary = await item_summary(my_item, photos)
            await query.message.answer_media_group(media=summary)
            await query.message.answer(text="Actions for the above 🔝 item", reply_markup=keyboard) 
        else:
            await query.message.answer("You do not have any posts")
async def handle_single_item_list_by_message(message: Message, callback_data: nav.SalesCallback, state: FSMContext):
    item_id, additional = int(callback_data.id), callback_data.additional
    async with SessionLocal() as session:
        my_item, photos = await rq.get_item_by_id(session, item_id)
        if my_item:
            keyboard = await nav.create_single_item_keyboard(my_item.id, my_item.title, photos)
            summary = await item_summary(my_item, photos)
            await message.answer_media_group(media=summary)
            await message.answer(text="Actions for the above 🔝 item", reply_markup=keyboard) 
        else:
            await message.answer("You do not have any posts")

@sales_router.callback_query(nav.SalesCallback.filter(F.action == "delete"))
async def handle_item_delete_by_query(query: CallbackQuery, callback_data: nav.SalesCallback, state: FSMContext):
    item_id = int(callback_data.id)
    additional = callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard(f"{additional}")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    print("ID", item_id)
    # Delete the item
    async with SessionLocal() as session:
        deleted_item = await rq.delete_item_by_id(session, item_id)
        if deleted_item:
            await query.answer("Deleted")
            # await query.message.answer("Job post successfully deleted")
            # await query.message.edit_reply_markup(ReplyKeyboardRemove())
            callback_data = nav.BlankCallback(text="Deleted")
            await my_items_by_query(query, callback_data, state)
        else:
            await query.answer("Error")
            callback_data = nav.BlankCallback(text="Error")
            await my_items_by_query(query, callback_data, state)


@sales_router.callback_query(nav.SalesCallback.filter(F.action == "edit"))
async def handle_item_edit_by_query(query: CallbackQuery, callback_data: nav.SalesCallback, state: FSMContext):
    await query.answer("Edit")
    item_id = int(callback_data.id)
    photos_string = callback_data.additional
    # additional = callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard("✏️ Edit")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    keyboard = await nav.create_edit_item_keyboard(item_id, photos_string)
    await query.message.answer("What do you want to edit?", reply_markup=keyboard)
@sales_router.callback_query(nav.SalesCallback.filter())
async def handle_item_field_edit_by_query(query: CallbackQuery, callback_data: nav.SalesCallback, state: FSMContext):
    item_id = int(callback_data.id)
    await state.set_state(SaleItemEdit.item_id)
    await state.update_data(item_id=item_id)
    photo_id = int(callback_data.additional)
    await state.set_state(SaleItemEdit.photo_id)
    await state.update_data(photo_id=photo_id)
    await query.answer(f"{callback_data.action.capitalize()}")
    match callback_data.action:
        case "title":
            updated_keyboard = await nav.create_blank_keyboard("title")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(SaleItemEdit.title)
            await query.message.answer("Provide new title")
        case "description":
            updated_keyboard = await nav.create_blank_keyboard("description")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(SaleItemEdit.description)
            await query.message.answer("Provide new description")
        case "price":
            updated_keyboard = await nav.create_blank_keyboard("price")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(SaleItemEdit.price)
            await query.message.answer("Provide new price")
        case "location":
            updated_keyboard = await nav.create_blank_keyboard("location")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(SaleItemEdit.location)
            await query.message.answer("Provide new location")
        case "photo1":
            updated_keyboard = await nav.create_blank_keyboard("photo 1")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(SaleItemEdit.photo1)
            await query.message.answer("Provide new photo")
        case "photo2":
            updated_keyboard = await nav.create_blank_keyboard("photo 2")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(SaleItemEdit.photo2)
            await query.message.answer("Provide new photo")
        case "photo3":
            updated_keyboard = await nav.create_blank_keyboard("photo 3")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(SaleItemEdit.photo3)
            await query.message.answer("Provide new photo")
        
@sales_router.message(SaleItemEdit.title, F.text)
@sales_router.message(SaleItemEdit.description, F.text)
@sales_router.message(SaleItemEdit.price, F.text)
@sales_router.message(SaleItemEdit.location, F.location)
@sales_router.message(SaleItemEdit.location, F.text)
@sales_router.message(SaleItemEdit.photo1, F.photo)
@sales_router.message(SaleItemEdit.photo2, F.photo)
@sales_router.message(SaleItemEdit.photo3, F.photo)
async def handle_item_field_update_callback(message: Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    item_id = data["item_id"]
    photo_id = data["photo_id"]
    callback_data = nav.SalesCallback(id=str(item_id), action="list", additional="")
    match current_state:
        case SaleItemEdit.title.state:
            print("ITEM ID", item_id)
            print("Current State", current_state)
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_item_by_id(session, item_id, SaleItemModel.title, message.text) 
                if updated:
                    await message.answer("Title successfully updated")
                    await handle_single_item_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case SaleItemEdit.description.state:
            async with SessionLocal() as session:
                updated = await rq.update_item_by_id(session, item_id, SaleItemModel.description, message.text) 
                if updated:
                    await message.answer("Description successfully updated")
                    await handle_single_item_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case SaleItemEdit.price.state:
            async with SessionLocal() as session:
                updated = await rq.update_item_by_id(session, item_id, SaleItemModel.price, message.text) 
                if updated:
                    await message.answer("Price successfully updated")
                    await handle_single_item_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case SaleItemEdit.location.state:
            if message.location:
                user_location = location.get_location(message.location.latitude, message.location.longitude)
                print(user_location)
                address = user_location[1]
                async with SessionLocal() as session:
                    updated = await rq.update_item_by_id(session, item_id, SaleItemModel.city, address)
                    if updated:
                        await message.answer("Location successfully updated")
                        await handle_single_item_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
            else:
                async with SessionLocal() as session:
                    updated = await rq.update_item_by_id(session, item_id, SaleItemModel.city, message.text) 
                    if updated:
                        await message.answer("City successfully updated")
                        await handle_single_item_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
        case SaleItemEdit.photo1.state:
            if message.photo:
                file_id = message.photo[-1].file_id
                async with SessionLocal() as session:
                    print("PHOTO", photo_id, "FILE_ID", file_id)
                    updated = await rq.update_item_photo_by_id(session, photo_id, file_id)
                    if updated:
                        await message.answer("Photo 1 successfully updated")
                        await handle_single_item_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
            else:
                await message.answer("Provide a photo")                         
        case SaleItemEdit.photo2.state:
            if message.photo:
                file_id = message.photo[-1].file_id
                async with SessionLocal() as session:
                    updated = await rq.update_item_photo_by_id(session, photo_id, file_id)
                    if updated:
                        await message.answer("Photo 2 successfully updated")
                        await handle_single_item_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
            else:
                await message.answer("Provide a photo") 
        case SaleItemEdit.photo3.state:
            if message.photo:
                file_id = message.photo[-1].file_id
                async with SessionLocal() as session:
                    updated = await rq.update_item_photo_by_id(session, photo_id, file_id)
                    if updated:
                        await message.answer("Photo 2 successfully updated")
                        await handle_single_item_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
            else:
                await message.answer("Provide a photo") 


# --- HELPER FUNCTIONS ---
async def item_summary(item: SaleItem, photos):
    summary = markdown.text(
                markdown.hbold(f'{item.title} |'),
                markdown.hunderline(f'{item.price}\n'),
                markdown.hitalic(f'{item.description}'),
                markdown.hbold(f'\nVendor ->'),
                markdown.hlink(f'@{item.username}', f'https://t.me/{item.username}'),
                markdown.hblockquote(f'📍 {item.city}'),
            )
    media = []
    for photo in photos:
        media.append(InputMediaPhoto(media=photo.photo_id))
    media[-1].caption = summary
    return media


# --- ERROR HANDLING --- 
    # choice = State()
    # searching = State()

    # title = State()
    # description = State()
    # photo1 = State()
    # photo2 = State()
    # photo3 = State()
    # price = State()
    # location = State()
    
@sales_router.message(Sales.choice)
async def choice_invalid(message: Message):
    await message.answer("I don't understand you. Please choose your action or Go /home")
@sales_router.message(Sales.searching)
async def searching_invalid(message: Message):
    await message.answer("I don't understand you")
@sales_router.message(SaleItem.title)
async def title_invalid(message: Message):
    await message.answer("I don't understand you")
@sales_router.message(SaleItem.description)
async def description_invalid(message: Message):
    await message.answer("I don't understand you")
@sales_router.message(SaleItem.photo1)
@sales_router.message(SaleItem.photo2)
@sales_router.message(SaleItem.photo3)
async def photos_invalid(message: Message):
    await message.answer("I don't understand you")
@sales_router.message(SaleItem.price)
async def price_invalid(message: Message):
    await message.answer("I don't understand you")
@sales_router.message(SaleItem.location)
async def location_invalid(message: Message):
    await message.answer("I don't understand you")

@sales_router.callback_query(nav.MenuCallback.filter(F.menu == "my_items"))
async def my_items_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@sales_router.callback_query(nav.MenuCallback.filter(F.menu == "post_item"))
async def post_item_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@sales_router.callback_query(nav.MenuCallback.filter(F.menu == "sales_go_search_beyond"))
async def go_search_beyond_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
# END




















    # job_skills: str = job.skills
    # skills_list: list = job_skills.split(',')
    # skills_formatted = "\n".join([f"- {skill.strip().capitalize()}" for skill in skills_list])
    # summary = (
    #     f"<b>{job.title}</b>\n\n"
    #     f"<code>{job.description}</code>\n\n"
    #     "Skills required:\n"
    #     f"{skills_formatted}\n\n"
    #     f"<i>📍 {(job.city).capitalize()}, {job.address}</i>"
    # )
    # return summary