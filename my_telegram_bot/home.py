from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command
from bot_info import set_back_commands, set_default_commands
import markups.markups as nav
from handlers.friendships_handler.friendships_markup import MenuCallback as friendsMenuCallback

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

@home_router.callback_query(friendsMenuCallback.filter(F.menu == "home"))
async def callback_home(query: CallbackQuery, callback_data: friendsMenuCallback):
    await query.answer("Home")
    text = "Choose category:" + " " * 50 + "&#x200D;" + '\n'
    await query.message.edit_text(text, reply_markup=nav.categoryChoiceMenu.as_markup())
    await set_default_commands(id=query.from_user.id)