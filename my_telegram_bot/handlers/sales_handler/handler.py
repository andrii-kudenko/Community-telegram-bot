from typing import Any, Dict
import logging

from aiogram import Router, F, html
from aiogram.utils.markdown import bold, italic, text, code, pre
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, InputMediaPhoto, FSInputFile
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from . import markup as nav
from utils import location
from bot_info import set_back_commands, set_default_commands
from home import home

sales_router = Router(name=__name__)

class Sales(StatesGroup):
    choice = State()
    searching = State()

class SaleItem(StatesGroup):
    title = State()
    description = State()
    price = State()
    location = State()

@sales_router.message(Command("sales", prefix=("!/")))
async def start_sales(message: Message, state: FSMContext):
    await state.set_state(Sales.choice)
    await message.answer("Hi there! Choose the action:", reply_markup=nav.salesChoiceMenu)

# sales_filter = SaleItem.title | SaleItem.description | SaleItem.price | SaleItem.location
@sales_router.message(SaleItem.title, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.description, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.price, Command("cancel", prefix=("!/")))
@sales_router.message(SaleItem.location, Command("cancel", prefix=("!/")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.set_state(Sales.choice)
    await message.answer(
        "Cancelled",
        reply_markup=nav.salesChoiceMenu,
    )
    await set_default_commands(id=message.from_user.id)

@sales_router.message(SaleItem.title, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.description, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.price, Command("back", prefix=("!/")))
@sales_router.message(SaleItem.location, Command("back", prefix=("!/")))
async def back_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == SaleItem.title:
            await state.set_state(Sales.choice)
            await message.answer("Choose action:", reply_markup=nav.salesChoiceMenu)
    elif current_state == SaleItem.description:
            await state.set_state(SaleItem.title)
            await message.answer("Send me new title")
    elif current_state == SaleItem.price:
            await state.set_state(SaleItem.description)
            await message.answer("Send me new description")
    elif current_state == SaleItem.location:
            await state.set_state(SaleItem.price)
            await message.answer("Send me new price")
    else:
         pass

@sales_router.message(Sales.choice, F.text == "Search 🔎")
async def search(message: Message, state: FSMContext):
    await message.answer("Searching...")
    await state.set_state(Sales.searching)
@sales_router.message(Sales.searching)
async def obtain_photo(message: Message, state: FSMContext):
    print(type(message.photo))
    print(len(message.photo))
    file_id = message.photo[-1].file_id
    title_1 = "First Photo Title"
    description_1 = "This is the description of the first photo."
    caption_1 = f"{title_1}\n{description_1}"
    
    title_2 = "Second Photo Title"
    description_2 = "This is the description of the second photo."
    caption_2 = f"*{title_2}*\n{description_2}"
    me = FSInputFile("me_hi.jpg")
    media = [
        InputMediaPhoto(media=file_id, caption=caption_1),
        InputMediaPhoto(media=me)
    ]
    print(type(file_id))
    print(len(file_id))
    await message.answer_media_group(media=media)
@sales_router.message(Sales.choice, F.text == "Post an ad 📦")
async def ad(message: Message, state: FSMContext):
    await message.answer("Creating your ad...\
                         \nMind that you can always \nGo /back or /cancel the process")                   
    await state.set_state(SaleItem.title)
    await message.answer("Type the title for your ad:", reply_markup=ReplyKeyboardRemove())
    await set_back_commands(id=message.from_user.id)
@sales_router.message(Sales.choice)
async def choice_invalid(message: Message):
    await message.answer("I don't understand you. Please choose your action or Go /home")

@sales_router.message(SaleItem.title, F.text)
async def ad_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(SaleItem.description)
    await message.answer(f"Now, provide some description:")
    
@sales_router.message(SaleItem.description, F.text)
async def ad_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(SaleItem.price)
    await message.answer(f"Ok, now set the price for your ad:")

@sales_router.message(SaleItem.price, F.text)
async def ad_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(SaleItem.location)
    await message.answer(f"Ok, now give the location for your ad:", reply_markup=nav.locationMenu)

@sales_router.message(SaleItem.location, F.location)
@sales_router.message(SaleItem.location, F.text)
async def ad_location(message: Message, state: FSMContext):
    if message.location:
        user_location = location.get_location(message.location.latitude, message.location.longitude)
        print(user_location)
        data = await state.update_data(location=user_location[1])
    else:
         data = await state.update_data(location=message.text)
    await state.clear()

    await show_summary(message=message, data=data)

    await state.set_state(Sales.choice)
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.salesChoiceMenu)
    await set_default_commands(id=message.from_user.id)
    await home(message)

async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
    title = data["title"]
    description = data["description"]
    price = data["price"]
    location = data["location"]
    summary = text(
        text(f"{html.underline('Item Information:\n')}"),
        text(f"{html.bold('Title:')} {title}\n"),
        text(f"{html.bold('Description:')} {html.italic(description)}\n"),
        text(f"{html.bold('Price:')} {html.code(price)}"),
        text(f"{html.blockquote(location)}"),
    )
    await message.answer(text=summary, reply_markup=ReplyKeyboardRemove())

# @sales_router.message()
# async def invalid_input(message: Message):
#      await message.answer("Please, provide a valid answer sales")