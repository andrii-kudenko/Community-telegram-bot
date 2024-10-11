from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot_info import set_back_commands, set_default_commands
import markups.markups as nav
from handlers.friendships_handler.friendships_markup import MenuCallback as friendsMenuCallback
from handlers.jobs_handler.jobs_markup import MenuCallback as jobsMenuCallback
from handlers.sales_handler.sales_handler import start_sales_by_query
from handlers.livings_handler.livings_handler import start_livings_by_query

home_router = Router(name=__name__)


@home_router.message(Command("home", prefix=("!/")))
async def home(message: Message) -> None:
    await message.answer("Home Menu", reply_markup=ReplyKeyboardRemove())
    text = "Choose category:" + " " * 50 + "&#x200D;" + '\n'
    print(text)
    await message.answer(text, reply_markup=nav.categoryChoiceMenu.as_markup())
    # my_message = await message.answer("Home")
    # print(my_message)
    # print(my_message.message_id)
    # await bot.edit_message_text(message_id=my_message.message_id, chat_id=my_message.chat.id, text="Choose a category:", reply_markup=nav.categoryChoiceMenu.as_markup())
    # await bot.edit_message_reply_markup()
    # await message.edit_text(inline_message_id=my_message.message_id, text="Choose a category:", reply_markup=nav.categoryChoiceMenu.as_markup())
    # await message.answer("Choose a category:", reply_markup=nav.categoryChoiceMenu.as_markup())
    await set_default_commands(id=message.from_user.id)
# MIDDLEWARE FOR SALES
@home_router.callback_query(nav.MenuCallback.filter(F.menu == "start_sales"))
async def sales_middleware(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    await query.answer("Sales")
    updated_keyboard = await nav.create_blank_keyboard("Sales 💵")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    username = query.from_user.username
    if username is None:
        await query.message.answer("You are required to have a username for this section. \nGo to telegram settings and add a username")
        await home(query.message)
    else:
        callback_data = nav.MenuCallback(menu="start_sales")
        await start_sales_by_query(query, callback_data, state)
# MIDDLEWARE FOR LIVINGS
@home_router.callback_query(nav.MenuCallback.filter(F.menu == "start_livings"))
async def livings_middleware(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    await query.answer("Livings")
    updated_keyboard = await nav.create_blank_keyboard("Livings 🛏")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    username = query.from_user.username
    if username is None:
        await query.message.answer("You are required to have a username for this section. \nGo to telegram settings and add a username")
        await home(query.message)
    else:
        callback_data = nav.MenuCallback(menu="start_livings")
        await start_livings_by_query(query, callback_data, state)



@home_router.callback_query(friendsMenuCallback.filter(F.menu == "home"))
@home_router.callback_query(jobsMenuCallback.filter(F.menu == "home"))
async def callback_home(query: CallbackQuery, callback_data: friendsMenuCallback):
    await query.answer("Home")
    text = "Choose category:" + " " * 50 + "&#x200D;" + '\n'
    await query.message.edit_text(text, reply_markup=nav.categoryChoiceMenu.as_markup())
    await set_default_commands(id=query.from_user.id)