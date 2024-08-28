from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# --- SEARCH ---
btnSearch = KeyboardButton(text='Search 🔎')
btnPost = KeyboardButton(text='Post an ad 📰')
btnMyPosts = KeyboardButton(text='View my job ads 🧾')
jobsReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost], [btnMyPosts]])

btnNext = KeyboardButton(text='Next ➡️')
nextMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnNext]])


# --- LOCATION ---
btnLocation = KeyboardButton(text='Provide Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])


# --- MENUS ---
class ApplyCallback(CallbackData, prefix="navigation"):
    action: str

class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

applyMenu = InlineKeyboardBuilder()
applyMenu.button(text='Apply 📨', callback_data=ApplyCallback(action="apply").pack())
appliedMenu = InlineKeyboardBuilder()
appliedMenu.button(text='Applied ✅', callback_data=ApplyCallback(action="applied").pack())

jobsChoiceMenu = InlineKeyboardBuilder() 
jobsChoiceMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
jobsChoiceMenu.button(text='Post job 📰', callback_data=MenuCallback(menu="post_job").pack())
jobsChoiceMenu.button(text='My job ads', callback_data=MenuCallback(menu="my_job_ads").pack())

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=MenuCallback(menu="jobs_go_search_beyond").pack())