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

class JobsCallback(CallbackData, prefix="job"):
    id: str
    action: str

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

async def create_jobs_keyboard(jobs):
    jobsAllMenu = InlineKeyboardBuilder()
    jobsAllMenu.button(text="Leave", callback_data=MenuCallback(menu="leave").pack())
    for job in jobs:
        jobsAllMenu.button(text=job.title, callback_data=JobsCallback(id=str(job.id), action="list").pack())
    jobsAllMenu.adjust(2)
    return jobsAllMenu.as_markup()

# jobsHandleMenu = InlineKeyboardBuilder()
# jobsHandleMenu.button(text="Back", callback_data=JobsCallback(action="back").pack())
# jobsHandleMenu.button(text="Edit", callback_data=JobsCallback(action="edit").pack())
# jobsHandleMenu.button(text="Edit", callback_data=JobsCallback(action="delete").pack())
async def create_single_job_keyboard(id):
    jobMenu = InlineKeyboardBuilder()
    jobMenu.button(text="Back", callback_data=JobsCallback(id=str(id), action="back").pack())
    jobMenu.button(text="Edit", callback_data=JobsCallback(id=str(id), action="edit").pack())
    jobMenu.button(text="Delete", callback_data=JobsCallback(id=str(id), action="delete").pack())
    jobMenu.adjust(2)
    return jobMenu.as_markup()

async def create_edit_job_keyboard(id):
    editMenu = InlineKeyboardBuilder()
    editMenu.button(text="Title", callback_data=JobsCallback(id=str(id), action="title").pack())
    editMenu.button(text="Description", callback_data=JobsCallback(id=str(id), action="description").pack())
    editMenu.button(text="Skills", callback_data=JobsCallback(id=str(id), action="skills").pack())
    editMenu.button(text="City", callback_data=JobsCallback(id=str(id), action="city").pack())
    editMenu.button(text="Address", callback_data=JobsCallback(id=str(id), action="address").pack())
    editMenu.adjust(2)
    return editMenu.as_markup()
