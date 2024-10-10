from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# --- MENUS ---
class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

class SalesCallback(CallbackData, prefix="sales"):
    action: str

class BlankCallback(CallbackData, prefix="empty"):
    text: str

# --- SEARCH ---
# btnSearch = KeyboardButton(text='Search 🔎')
# btnPost = KeyboardButton(text='Post an ad 📦')
# btnMyPosts = KeyboardButton(text='View my sale ads🧾')
# salesReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost], [btnMyPosts]])
salesReplyChoiceMenu = InlineKeyboardBuilder()
salesReplyChoiceMenu.button(text="Search 🔎", callback_data=SalesCallback(action="search").pack())
salesReplyChoiceMenu.button(text="Post an ad 📦", callback_data=SalesCallback(action="post_item").pack())
salesReplyChoiceMenu.button(text="View my sale ads🧾", callback_data=MenuCallback(menu="my_items").pack())

btnNext = KeyboardButton(text='Next ➡️')
nextMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnNext]])


# --- HANDLE PHOTOS ---
btnSavePhoto1 = KeyboardButton(text='Continue with 1/3 photos')
photosUploadingReplyMenu1 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto1]])
btnSavePhoto2 = KeyboardButton(text='Continue with 2/3 photos')
photosUploadingReplyMenu2 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto2]])


# --- LOCATION ---
btnLocation = KeyboardButton(text='Provide Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])




salesChoiceMenu = InlineKeyboardBuilder() # When there are no more profiles to look
salesChoiceMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
salesChoiceMenu.button(text='Post item 📰', callback_data=SalesCallback(action="post_item").pack())
salesChoiceMenu.button(text='My items', callback_data=MenuCallback(menu="my_items").pack())
salesChoiceMenu.adjust(2,1)

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=SalesCallback(action="search_beyond").pack())

async def create_blank_keyboard(text):
    blankMenu = InlineKeyboardBuilder()
    blankMenu.button(text=f"{text}", callback_data=BlankCallback(text=f"{text}").pack())
    return blankMenu.as_markup()