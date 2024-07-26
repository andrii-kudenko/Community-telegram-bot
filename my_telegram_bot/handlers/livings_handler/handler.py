from typing import Any, Dict
import logging

from aiogram import Router, F, html
from aiogram.utils.markdown import bold, italic, text, code, pre
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from . import markup as nav
from utils import location
from bot_info import set_back_commands, set_default_commands

living_router = Router(name=__name__)

class Livings(StatesGroup):
    choice = State()
    searching = State()

class Living(StatesGroup):
    title = State()
    description = State()
    price = State()
    location = State()

@living_router.message(Command("livings", prefix=("!/")))
async def start_livings(message: Message, state: FSMContext):
    await state.set_state(Livings.choice)
    await message.answer("Hi there! Choose the action:", reply_markup=nav.livingsChoiceMenu)

@living_router.message(Living.title, Command("cancel", prefix=("!/")))
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

@living_router.message(Living.title, Command("back", prefix=("!/")))
@living_router.message(Living.description, Command("back", prefix=("!/")))
@living_router.message(Living.price, Command("back", prefix=("!/")))
@living_router.message(Living.location, Command("back", prefix=("!/")))
async def back_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Living.title:
            await state.set_state(Livings.choice)
            await message.answer("Choose action:", reply_markup=nav.livingsChoiceMenu)
    elif current_state == Living.description:
            await state.set_state(Living.title)
            await message.answer("Send me new title")
    elif current_state == Living.price:
            await state.set_state(Living.description)
            await message.answer("Send me new description")
    elif current_state == Living.location:
            await state.set_state(Living.price)
            await message.answer("Send me new price")

@living_router.message(Livings.choice, F.text == "Search 🔎")
async def search(message: Message, state: FSMContext):
    await message.answer("Searching...")
    await state.set_state(Livings.searching)
@living_router.message(Livings.choice, F.text == "Post an ad 📰")
async def living(message: Message, state: FSMContext):
    await message.answer("Creating your ad...\
                         \nMind that you can always \nGo /back or /cancel the process")
    await state.set_state(Living.title)
    await message.answer("Type the title for your ad:", reply_markup=ReplyKeyboardRemove())
    await set_back_commands(id=message.from_user.id)
@living_router.message(Livings.choice)
async def choice_invalid(message: Message):
    await message.answer("I don't understand you. Please choose your action or Go /home")

@living_router.message(Living.title, F.text)
async def living_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(Living.description)
    await message.answer(f"Now, provide some description:")
    
@living_router.message(Living.description, F.text)
async def living_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Living.price)
    await message.answer(f"Ok, now provide price for your ad:")

@living_router.message(Living.price, F.text)
async def living_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(Living.location)
    await message.answer(f"Ok, now give the location for your place:", reply_markup=nav.locationMenu)

@living_router.message(Living.location, F.location)
@living_router.message(Living.location, F.text)
async def living_location(message: Message, state: FSMContext):
    if message.location:
        user_location = location.get_location(message.location.latitude, message.location.longitude)
        print(user_location)
        data = await state.update_data(location=user_location[1])
    else:
         data = await state.update_data(location=message.text)
    await state.clear()

    await show_summary(message=message, data=data)

    await state.set_state(Livings.choice)
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.livingsChoiceMenu)
    await set_default_commands(id=message.from_user.id)

async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
    title = data["title"]
    description = data["description"]
    price = data["price"]
    location = data["location"]
    summary = text(
        text(f"{html.underline('Ad overview:\n')}"),
        text(f"{html.bold('Title:')} {title}\n"),
        text(f"{html.bold('Description:')} {html.italic(description)}\n"),
        text(f"{html.bold('Price:')} {html.code(price)}"),
        text(f"{html.blockquote(location)}"),
    )
    await message.answer(text=summary, reply_markup=ReplyKeyboardRemove())

# @living_router.message()
# async def invalid_input(message: Message):
#      await message.answer("Please, provide a valid answer livings")