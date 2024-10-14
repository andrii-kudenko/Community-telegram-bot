from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# --- MENUS ---
class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

class FriendsCallback(CallbackData, prefix="frineds"):
    action: str

class BlankCallback(CallbackData, prefix="empty"):
    text: str

# --- SEARCH ---
# btnSearch = KeyboardButton(text='Search 🔎')
# btnBio = KeyboardButton(text='My Bio 👤')
# friendsReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnBio]])
# btnNewBio = KeyboardButton(text='New Bio 👤')
# bioReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnNewBio]])
friendsReplyChoiceMenu = InlineKeyboardBuilder()
friendsReplyChoiceMenu.button(text="Search 🔎", callback_data=FriendsCallback(action="search").pack())
friendsReplyChoiceMenu.button(text="My Bio 👤", callback_data=MenuCallback(menu="my_bio").pack())
friendsReplyChoiceMenu.button(text="Something", callback_data=FriendsCallback(action="something").pack())
friendsReplyChoiceMenu.button(text="Go home 🏠", callback_data=MenuCallback(menu="home").pack())
friendsReplyChoiceMenu.adjust(2, 1)



btnLike = KeyboardButton(text='👍')
btnDisLike = KeyboardButton(text='👎')
likeMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLike], [btnDisLike]])


# --- HANDLE PHOTOS ---
btnSavePhoto1 = KeyboardButton(text='Continue with 1/3 photos')
photosUploadingReplyMenu1 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto1]])
btnSavePhoto2 = KeyboardButton(text='Continue with 2/3 photos')
photosUploadingReplyMenu2 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto2]])


# --- LOCATION ---
btnLocation = KeyboardButton(text='Provide Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])




homeChoiceMenu = InlineKeyboardBuilder() # When there are no more profiles to look
homeChoiceMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
homeChoiceMenu.button(text='My Bio 👤', callback_data=MenuCallback(menu="my_bio").pack())
homeChoiceMenu.adjust(2,1)

bioChangeMenu = InlineKeyboardBuilder() 
bioChangeMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
bioChangeMenu.button(text='New Bio 👤', callback_data=FriendsCallback(action="new_bio").pack())
bioChangeMenu.button(text='Search 🔎', callback_data=FriendsCallback(action="search").pack())

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=FriendsCallback(action="search_beyond").pack())

# NOT USED
showUserMenu = InlineKeyboardBuilder() 
showUserMenu.button(text='👀', callback_data=MenuCallback(menu="liked_by_someone").pack())

async def create_blank_keyboard(text):
    blankMenu = InlineKeyboardBuilder()
    blankMenu.button(text=f"{text}", callback_data=BlankCallback(text=f"{text}").pack())
    return blankMenu.as_markup()