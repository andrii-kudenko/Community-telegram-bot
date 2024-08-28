from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# --- SEARCH ---
btnSearch = KeyboardButton(text='Search 🔎')
btnBio = KeyboardButton(text='My Bio 👤')
friendsReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnBio]])
btnNewBio = KeyboardButton(text='New Bio 👤')
bioReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnNewBio]])

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


# --- MENUS ---
class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

homeChoiceMenu = InlineKeyboardBuilder() # When there are no more profiles to look
homeChoiceMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
homeChoiceMenu.button(text='My Bio 👤', callback_data=MenuCallback(menu="my_bio").pack())
homeChoiceMenu.adjust(2,1)

bioChangeMenu = InlineKeyboardBuilder() 
bioChangeMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
bioChangeMenu.button(text='New Bio 👤', callback_data=MenuCallback(menu="new_bio").pack())
bioChangeMenu.button(text='Search 🔎', callback_data=MenuCallback(menu="friendships_go_search").pack())

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=MenuCallback(menu="friendships_go_search_beyond").pack())

# NOT USED
showUserMenu = InlineKeyboardBuilder() 
showUserMenu.button(text='👀', callback_data=MenuCallback(menu="liked_by_someone").pack())