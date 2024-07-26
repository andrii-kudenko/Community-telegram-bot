from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

btnSearch = KeyboardButton(text='Search 🔎')
btnPost = KeyboardButton(text='Post an ad 📦')
salesChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost]])

btnLocation = KeyboardButton(text='Get Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])
