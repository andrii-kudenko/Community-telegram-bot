from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# --- SEARCH ---
btnSearch = KeyboardButton(text='Search 🔎')
btnPost = KeyboardButton(text='Post an ad 📰')
btnMyPosts = KeyboardButton(text='View my living ads 🧾')
livingsReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost], [btnMyPosts]])

btnNext = KeyboardButton(text='Next ➡️')
nextMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnNext]])


# --- HANDLE PHOTOS ---
btnSavePhoto1 = KeyboardButton(text='Continue with 1/6 photos')
photosUploadingReplyMenu1 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto1]])
btnSavePhoto2 = KeyboardButton(text='Continue with 2/6 photos')
photosUploadingReplyMenu2 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto2]])
btnSavePhoto3 = KeyboardButton(text='Continue with 3/6 photos')
photosUploadingReplyMenu3 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto3]])
btnSavePhoto4 = KeyboardButton(text='Continue with 4/6 photos')
photosUploadingReplyMenu4 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto4]])
btnSavePhoto5 = KeyboardButton(text='Continue with 5/6 photos')
photosUploadingReplyMenu5 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto5]])


# --- LOCATION ---
btnLocation = KeyboardButton(text='Provide Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])


# --- MENUS ---
class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

livingsChoiceMenu = InlineKeyboardBuilder() # When there are no more profiles to look
livingsChoiceMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
livingsChoiceMenu.button(text='Post living 📰', callback_data=MenuCallback(menu="post_living").pack())
livingsChoiceMenu.button(text='My livings', callback_data=MenuCallback(menu="my_livings").pack())
livingsChoiceMenu.adjust(2,1)

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=MenuCallback(menu="livings_go_search_beyond").pack())