# IDEA: 
# when having options from the same city, check if coordinates are give, if yes, calculate the distance
# need to create a separate handler for my posts

from typing import Any, Dict
import logging

from aiogram import Router, F, html
from aiogram.utils import markdown
from aiogram.utils.markdown import bold, italic, text, code, pre
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from . import jobs_markup as nav
from markups import markups
from utils import location
from bot_info import set_back_commands, set_default_commands
from database import jobs_requests as rq
from database.models import SessionLocal
from database.models import Job

# from handlers.friendships_handler.friendships_markup import MenuCallback as friendsMenuCallback
# from friendships_handler.friendships_markup import MenuCallback

job_router = Router(name=__name__)

class NewJob():
     def __init__(self, coordinates, user_id, title, description, skills, city, address, latitude = 0, longtitude = 0) -> None:
          self.coordinates = coordinates
          self.user_id = user_id
          self.title = title
          self.description = description
          self.skills = skills
          self.latitude = latitude
          self.longtitude = longtitude
          self.city = city
          self.address = address

class Jobs(StatesGroup):
    choice = State()
    searching = State()

class Job(StatesGroup):
    title = State()
    description = State()
    skills = State()
    location = State()
    # optional
    address = State()

    # ---UTILITY FUNCTIONS---
search_funcitons_map = { # execute appropriate function depending on the city_search value in user
    True: rq.get_next_job_by_id_with_city,
    False: rq.get_next_job_by_id_without_city
}
# update_funcitons_map = { # execute appropriate function depending on the city_search value in bio
#     True: rq.update_my_search_id,
#     False: rq.update_my_beyond_city_search_id
# }


# --- COMMANDS ---
@job_router.message(Command("jobs", prefix=("!/")))
async def start_jobs(message: Message, state: FSMContext):
    await state.set_state(Jobs.choice)
    await message.answer("Hi there! Choose the action:", reply_markup=nav.jobsReplyChoiceMenu)

@job_router.message(Job.title, Command("cancel", prefix=("!/")))
@job_router.message(Job.description, Command("cancel", prefix=("!/")))
@job_router.message(Job.skills, Command("cancel", prefix=("!/")))
@job_router.message(Job.location, Command("cancel", prefix=("!/")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.set_state(Jobs.choice)
    await message.answer(
        "Cancelled",
        reply_markup=nav.jobsChoiceMenu,
    )
    await set_default_commands(id=message.from_user.id)

@job_router.message(Job.title, Command("back", prefix=("!/")))
@job_router.message(Job.description, Command("back", prefix=("!/")))
@job_router.message(Job.skills, Command("back", prefix=("!/")))
@job_router.message(Job.location, Command("back", prefix=("!/")))
async def back_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Job.title:
            await state.set_state(Jobs.choice)
            await message.answer("Choose action:", reply_markup=nav.jobsReplyChoiceMenu)
    elif current_state == Job.description:
            await state.set_state(Job.title)
            await message.answer("Send me new title")
    elif current_state == Job.skills:
            await state.set_state(Job.description)
            await message.answer("Send me new description")
    elif current_state == Job.location:
            await state.set_state(Job.skills)
            await message.answer("Send me new skills")


# --- SEARCH ---
@job_router.message(Jobs.choice, F.text == "Search 🔎")
async def search_by_message(message: Message, state: FSMContext): 
    user_id = message.from_user.id
    # database check for resume
    async with SessionLocal() as session:
        await rq.update_my_jobs_city_search(session, user_id, True)
    await message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Jobs.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        job = await rq.get_next_job_by_id_with_city(session, user.jobs_search_id_list, user.city)
        if job:
            summary = await post_summary(job)
            await message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
            await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
        elif job is None:
            await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
            await message.answer("Would you like to search job options outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
        else:
            await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
            await message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  
# @job_router.callback_query(nav.MenuCallback.filter(F.menu == "go_search"))
# async def search_by_query(query: CallbackQuery, state: FSMContext):
#     await query.answer("Searching")
#     user_id = query.from_user.id
#     # database check for resume
#     await query.message.answer("Searching...", reply_markup=nav.nextMenu)
#     await state.set_state(Jobs.searching)
#     async with SessionLocal() as session:
#         user = await rq.get_user(session, user_id)
#         job = await rq.get_next_job_by_id_with_city(session, user.jobs_search_id_list, user.city)
#         if job: 
#             summary = await post_summary(job)
#             await query.message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
#             await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
#         if job is None:
#             await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
#             await query.message.answer("You can come later to see new available job vacations", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
#         else:
#             await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
#             await query.message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  
@job_router.callback_query(nav.MenuCallback.filter(F.menu == "jobs_go_search_beyond"))
async def search_beyond_by_query(query: CallbackQuery, state: FSMContext):
    await query.answer("Searching outside")
    user_id = query.from_user.id
    async with SessionLocal() as session:
        await rq.update_my_jobs_city_search(session, user_id, False)
    await query.message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Jobs.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        job = await rq.get_next_job_by_id_without_city(session, user.jobs_search_id_list, user.city)
        if job:
            summary = await post_summary(job)
            await query.message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
            await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
        else:
            await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  


# --- MY POSTS ---
@job_router.message(Jobs.choice, F.text == "View my job ads 🧾")
async def my_job_posts_by_message(message: Message, state: FSMContext):
    # make a database request
    # and further manipulations
    async with SessionLocal() as session:
        new_job = await rq.test_add_job_post_to_user(session)
        print(new_job)
    await message.answer("My posts")
@job_router.callback_query(nav.MenuCallback.filter(F.menu == "my_job_ads"))
async def my_job_posts_by_query(message: Message, state: FSMContext):
    # make a database request
    # and further manipulations
    async with SessionLocal() as session:
        new_job = await rq.test_add_job_post_to_user(session)
        print(new_job)
    await message.answer("My posts")

# ---NEW POST---
@job_router.message(Jobs.choice, F.text == "Post an ad 📰")
async def job(message: Message, state: FSMContext):
    await message.answer("Creating your ad...\
                         \nMind that you can always \nGo /back or /cancel the process")
    await state.set_state(Job.title)
    await message.answer("Type the title for your ad:", reply_markup=ReplyKeyboardRemove())
    await set_back_commands(id=message.from_user.id)


# --- POST CREATION ---
@job_router.message(Job.title, F.text)
async def job_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(Job.description)
    await message.answer(f"Now, provide some description for {html.bold(message.text)}:")
@job_router.message(Job.description, F.text)
async def job_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Job.skills)
    await message.answer("Ok, now provide skills that are required for your job:")
@job_router.message(Job.skills, F.text)
async def job_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(Job.location)
    await message.answer(f"Ok, now provide the location for your job:", reply_markup=nav.locationMenu)
@job_router.message(Job.location, F.location)
async def job_location(message: Message, state: FSMContext):
    user_location = location.get_location(message.location.latitude, message.location.longitude)
    print(user_location)
    await state.update_data(location=user_location[1])
    data = await state.update_data(address=user_location[0])
    new_job = NewJob(True, message.from_user.id, data["title"], data["description"], data["skills"], data["location"], data["address"], message.location.latitude, message.location.longitude)
    await state.clear()
    await show_summary(message=message, data=data)
    # make database request to add post
    async with SessionLocal() as session:
        job_post = await rq.add_job_post_to_user(session, new_job)
        print("Job post added successfully", job_post)
    await state.set_state(Jobs.choice)
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.jobsReplyChoiceMenu)
    await set_default_commands(id=message.from_user.id)
@job_router.message(Job.location, F.text)
async def job_city(message: Message, state: FSMContext):
    city = message.text.strip().capitalize()
    await state.update_data(location=city)
    await state.set_state(Job.address)
    await message.answer("Add an address (street) for your post")
@job_router.message(Job.address, F.text)
async def job_address(message: Message, state: FSMContext):
    data = await state.update_data(address=message.text)
    new_job = NewJob(False, message.from_user.id, data["title"], data["description"], data["skills"], data["location"], data["address"])
    await state.clear()
    await show_summary(message=message, data=data)
    # make database request to add post
    async with SessionLocal() as session:
        job_post = await rq.add_job_post_to_user(session, new_job)
        print("Job post added successfully", job_post)
    await state.set_state(Jobs.choice)
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.jobsReplyChoiceMenu)

async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
    title = data["title"]
    description = data["description"]
    skills = data["skills"]
    location = data["location"]
    # summary = text(
    #     text(f"{html.underline('Job overview:\n')}"),
    #     text(f"{html.bold('Title:')} {title}\n"),
    #     text(f"{html.bold('Description:')} {html.italic(description)}\n"),
    #     text(f"{html.bold('Skills (required):')} {html.code(skills)}"),
    #     text(f"{html.blockquote(location)}"),
    # )
    summary = markdown.text(
                markdown.hbold(f'{title}\n'),
                markdown.hcode(f'{description}\n'),
                markdown.text('Skills required:'),
                markdown.hitalic(f'{skills}'),
                markdown.hblockquote(f'{location}')
            )
    await message.answer(text=summary, reply_markup=ReplyKeyboardRemove())


# --- NEXT ---
@job_router.message(Jobs.searching, F.text == "Next ➡️")
async def next_job(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # await state.set_state(Jobs.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        # job = await rq.get_next_job_by_id(session, user.jobs_search_id_list)
        job = await search_funcitons_map[user.jobs_city_search](session, user.jobs_search_id_list, user.city)
        if job:
            summary = await post_summary(job)
            await message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
            await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
        elif job is None:
            if user.jobs_city_search:
                await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
                await message.answer("Would you like to search job options outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
            else:
                await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
                await message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  
        else:
            await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
            await message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  


# --- JOB APPLICATION ---
@job_router.callback_query(Jobs.searching, nav.ApplyCallback.filter(F.action == "apply"))
async def apply_for_job(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    async with SessionLocal() as session:
         user = await rq.get_user(session, user_id)
         job_application = await rq.apply_for_job(session, user.jobs_search_id, user.user_id)
    await query.answer('Applied')
    await query.message.edit_reply_markup(reply_markup=nav.appliedMenu.as_markup())
@job_router.callback_query(Jobs.searching, nav.ApplyCallback.filter(F.action == "applied"))
async def applied(query: CallbackQuery, state: FSMContext):
    await query.answer("Already Applied")


# --- HELPER FUNCTIONS ---
async def post_summary(job: Job): # use ParseMode.HTML (parse_mode=ParseMode.HTML)
    job_skills: str = job.skills
    skills_list: list = job_skills.split(',')
    skills_formatted = "\n".join([f"- {skill.strip().capitalize()}" for skill in skills_list])
    summary = (
        f"<b>{job.title}</b>\n\n"
        f"<code>{job.description}</code>\n\n"
        "Skills required:\n"
        f"{skills_formatted}\n\n"
        f"<i>📍 {(job.city).capitalize()}, {job.address}</i>"
    )
    return summary


# --- ERROR HANDLING --- 
    # choice = State()
    # searching = State()

    # title = State()
    # description = State()
    # skills = State()
    # location = State()
    # # optional
    # address = State()
    
@job_router.message(Jobs.choice)
async def choice_invalid(message: Message):
    await message.answer("I don't understand you. Please choose your action or Go /home")
@job_router.message(Jobs.searching)
async def searching_invalid(message: Message):
    await message.answer("I don't understand you")
@job_router.message(Job.title)
async def title_invalid(message: Message):
    await message.answer("I don't understand you")
@job_router.message(Job.description)
async def description_invalid(message: Message):
    await message.answer("I don't understand you")
@job_router.message(Job.skills)
async def skills_invalid(message: Message):
    await message.answer("I don't understand you")
@job_router.message(Job.location)
async def location_invalid(message: Message):
    await message.answer("I don't understand you")
@job_router.message(Job.address)
async def address_invalid(message: Message):
    await message.answer("I don't understand you")

@job_router.callback_query(nav.ApplyCallback.filter(F.menu == "apply"))
async def apply_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@job_router.callback_query(nav.ApplyCallback.filter(F.menu == "applied"))
async def applied_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")

@job_router.callback_query(nav.MenuCallback.filter(F.menu == "post_job"))
async def post_job_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@job_router.callback_query(nav.MenuCallback.filter(F.menu == "my_job_ads"))
async def my_bio_ads_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
@job_router.callback_query(nav.MenuCallback.filter(F.menu == "jobs_go_search_beyond"))
async def go_search_beyond_invalid(query: CallbackQuery):
    await query.message.answer("I don't understand")
# END




















    # await message.answer("Searching...")
    # job_title = "Software Developer"
    # job_description = "We are looking for a skilled software developer to join our team. The ideal candidate will have experience in developing scalable web applications and a strong understanding of software development principles."
    # job_skills = ["Python", "JavaScript", "SQL", "HTML/CSS", "Git", "Agile methodology"]
    # job_location = "Remote or On-site in San Francisco, CA"

    # skills_formatted = "\n".join([f"- {skill}" for skill in job_skills])

    # summary = (
    #     f"<b>{job_title}</b>\n\n"
    #     f"<code>{job_description}</code>\n\n"
    #     "Skills required:\n"
    #     f"{skills_formatted}\n\n"
    #     f"<i>{job_location}</i>"
    # )

