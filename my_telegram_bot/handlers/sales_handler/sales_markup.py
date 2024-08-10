from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

btnSearch = KeyboardButton(text='Search 🔎')
btnPost = KeyboardButton(text='Post an ad 📦')
salesReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost]])

btnSavePhoto1 = KeyboardButton(text='Continue with 1/3 photos')
photosUploadingReplyMenu1 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto1]])
btnSavePhoto2 = KeyboardButton(text='Continue with 2/3 photos')
photosUploadingReplyMenu2 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto2]])

btnLocation = KeyboardButton(text='Provide Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])

btnNext = KeyboardButton(text='Next ➡️')
nextMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnNext]])

class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

salesChoiceMenu = InlineKeyboardBuilder() # When there are no more profiles to look
salesChoiceMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
salesChoiceMenu.button(text='My items', callback_data=MenuCallback(menu="my_items").pack())
salesChoiceMenu.adjust(2,1)

bioChangeMenu = InlineKeyboardBuilder() 
bioChangeMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
# bioChangeMenu.button(text='New Bio 👤', callback_data=MenuCallback(menu="new_bio").pack())
bioChangeMenu.button(text='Search 🔎', callback_data=MenuCallback(menu="sales_go_search").pack())

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=MenuCallback(menu="sales_go_search_beyond").pack())

