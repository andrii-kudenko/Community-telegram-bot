from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# --- SEARCH ---
# btnSearch = KeyboardButton(text='Search 🔎')
# btnPost = KeyboardButton(text='Post an ad 📰')
# btnMyPosts = KeyboardButton(text='View my job ads 🧾')
# jobsReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost], [btnMyPosts]])



btnNext = KeyboardButton(text='Next ➡️')
nextMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnNext]])

btnSkip = KeyboardButton(text="Skip")
skipMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSkip]])


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
    additional: str

class BlankCallback(CallbackData, prefix="empty"):
    text: str

class ApplicantsCallback(CallbackData, prefix="applicant"):
    id: str
    action: str
    job_id: str

jobsReplyChoiceMenu = InlineKeyboardBuilder()
jobsReplyChoiceMenu.button(text="Search 🔎", callback_data=JobsCallback(id="0", action="search", additional="").pack())
jobsReplyChoiceMenu.button(text="Post an ad 📰", callback_data=JobsCallback(id="0", action="post_ad", additional="").pack())
jobsReplyChoiceMenu.button(text="View my job ads 🧾", callback_data=MenuCallback(menu="my_job_ads").pack())
jobsReplyChoiceMenu.button(text="Go home 🏠", callback_data=MenuCallback(menu="home").pack())
jobsReplyChoiceMenu.adjust(2, 1)


applyMenu = InlineKeyboardBuilder()
applyMenu.button(text='Apply 📨', callback_data=ApplyCallback(action="apply").pack())
appliedMenu = InlineKeyboardBuilder()
appliedMenu.button(text='Applied ✅', callback_data=ApplyCallback(action="applied").pack())

jobsChoiceMenu = InlineKeyboardBuilder() 
jobsChoiceMenu.button(text='Home 🏠', callback_data=MenuCallback(menu="home").pack())
jobsChoiceMenu.button(text='Post job 📰', callback_data=JobsCallback(id="0", action="post_ad", additional="").pack())
jobsChoiceMenu.button(text='My job ads', callback_data=MenuCallback(menu="my_job_ads").pack())
jobsChoiceMenu.adjust(2)

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=MenuCallback(menu="jobs_go_search_beyond").pack())

async def create_jobs_keyboard(jobs):
    jobsAllMenu = InlineKeyboardBuilder()
    for job in jobs:
        jobsAllMenu.button(text=job.title, callback_data=JobsCallback(id=str(job.id), action="manage", additional=f"{job.title}").pack())
    jobsAllMenu.button(text="Back", callback_data=JobsCallback(id=str(job.id), action="start_jobs", additional="").pack())
    jobsAllMenu.adjust(2)
    return jobsAllMenu.as_markup()

# jobsHandleMenu = InlineKeyboardBuilder()
# jobsHandleMenu.button(text="Back", callback_data=JobsCallback(action="back").pack())
# jobsHandleMenu.button(text="Edit", callback_data=JobsCallback(action="edit").pack())
# jobsHandleMenu.button(text="Edit", callback_data=JobsCallback(action="delete").pack())
async def create_single_job_keyboard(id, title):
    jobMenu = InlineKeyboardBuilder()
    jobMenu.button(text="✏️ Edit", callback_data=JobsCallback(id=str(id), action="edit", additional=title).pack())
    jobMenu.button(text="🖱️ Check applicants", callback_data=JobsCallback(id=str(id), action="check_applicants", additional=title).pack()) # 📩 🗒️ 🧾
    jobMenu.button(text="🗑️ Delete", callback_data=JobsCallback(id=str(id), action="delete", additional=title).pack()) # ❌
    jobMenu.button(text="Back", callback_data=JobsCallback(id="0", action="my_job_ads", additional="Back").pack())
    jobMenu.adjust(2)
    return jobMenu.as_markup()

async def create_edit_job_keyboard(id):
    editMenu = InlineKeyboardBuilder()
    editMenu.button(text="Title", callback_data=JobsCallback(id=str(id), action="title", additional="").pack())
    editMenu.button(text="Description", callback_data=JobsCallback(id=str(id), action="description", additional="").pack())
    editMenu.button(text="Skills", callback_data=JobsCallback(id=str(id), action="skills", additional="").pack())
    editMenu.button(text="City", callback_data=JobsCallback(id=str(id), action="city", additional="").pack())
    editMenu.button(text="Address", callback_data=JobsCallback(id=str(id), action="address", additional="").pack())
    editMenu.adjust(2)
    return editMenu.as_markup()

async def create_job_applicants_keyboard(job_applicants, job_id):
    applicantsMenu = InlineKeyboardBuilder()
    for resume in job_applicants:
        applicantsMenu.button(text=resume.full_name, callback_data=ApplicantsCallback(id=str(resume.id), job_id=str(job_id), action="review_applicant").pack())
    applicantsMenu.button(text="Back", callback_data=JobsCallback(id=str(job_id), action="manage", additional="Back").pack())
    # applicantsMenu.button(text="Home 🏠", callback_data=MenuCallback(menu="home").pack())
    applicantsMenu.adjust(1)
    return applicantsMenu.as_markup()

async def create_single_applicant_keyboard(applicant_id, job_id):
    applicantMenu = InlineKeyboardBuilder()
    applicantMenu.button(text="Back", callback_data=JobsCallback(id=str(job_id), action="check_applicants", additional="🖱️ Check applicants").pack())
    # applicantMenu.button(text="Next", callback_data=ApplicantsCallback(id=str(applicant_id), job_id=str(job_id), action="next").pack())
    applicantMenu.adjust(2)
    return applicantMenu.as_markup()


async def create_blank_keyboard(text):
    blankMenu = InlineKeyboardBuilder()
    blankMenu.button(text=f"{text}", callback_data=BlankCallback(text=f"{text}").pack())
    return blankMenu.as_markup()