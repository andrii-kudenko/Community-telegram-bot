from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

btnSearch = KeyboardButton(text='Search 🔎')
btnPost = KeyboardButton(text='Post an ad 📰')
jobsReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost]])

btnLocation = KeyboardButton(text='Provide Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])
