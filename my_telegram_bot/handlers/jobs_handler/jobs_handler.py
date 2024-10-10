# IDEA: 
# when having options from the same city, check if coordinates are give, if yes, calculate the distance
# need to create a separate handler for my posts

from typing import Any, Dict
import logging

from aiogram import Router, F, html
from aiogram.utils import markdown
from aiogram.utils.markdown import bold, italic, text, code, pre
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, User, Chat
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from . import jobs_markup as nav
from markups import markups
from utils import location
from bot_info import set_back_commands, set_default_commands
from database import jobs_requests as rq
from database.models import SessionLocal
from database.models import Job as JobModel

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
class JobEdit(StatesGroup):
    job_id = State()
    chat_instance = State()
    title = State()
    description = State()
    skills = State()
    location = State()
    address = State()

# class UpdateJob(StatesGroup):
#     title = State()
#     description = State()
#     skills = State()
#     location = State()
#     # optional
#     address = State()

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
    await message.answer("Hi there! Choose the action:", reply_markup=nav.jobsReplyChoiceMenu.as_markup())
@job_router.callback_query(nav.MenuCallback.filter(F.menu == "start_jobs"))
@job_router.callback_query(nav.JobsCallback.filter(F.action == "start_jobs"))
async def start_jobs_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    await query.answer("Jobs")
    if "menu" in callback_data.model_dump():
        updated_keyboard = await nav.create_blank_keyboard("Jobs 💻")
    else:
        updated_keyboard = await nav.create_blank_keyboard("Back")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    # await state.set_state(Jobs.choice)
    # await query.message.delete()
    await query.message.answer("Hi there! Choose the action:", reply_markup=nav.jobsReplyChoiceMenu.as_markup())

@job_router.message(Job.title, Command("cancel", prefix=("!/")))
@job_router.message(Job.description, Command("cancel", prefix=("!/")))
@job_router.message(Job.skills, Command("cancel", prefix=("!/")))
@job_router.message(Job.location, Command("cancel", prefix=("!/")))
@job_router.message(Job.address, Command("cancel", prefix=("!/")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.set_state(Jobs.choice)
    await message.answer(
        "Cancelled",
        reply_markup=nav.jobsReplyChoiceMenu.as_markup(),
    )
    await set_default_commands(id=message.from_user.id)

@job_router.message(Job.title, Command("back", prefix=("!/")))
@job_router.message(Job.description, Command("back", prefix=("!/")))
@job_router.message(Job.skills, Command("back", prefix=("!/")))
@job_router.message(Job.location, Command("back", prefix=("!/")))
@job_router.message(Job.address, Command("back", prefix=("!/")))
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
    elif current_state == Job.location:
            await state.set_state(Job.skills)
            await message.answer("Send me new skills")
    elif current_state == Job.address:
            await state.set_state(Job.location)
            await message.answer("Send me new location")



# --- SEARCH ---
@job_router.callback_query(nav.JobsCallback.filter(F.action == "search"))
async def search_by_query(query: CallbackQuery, state: FSMContext): 
    user_id = query.from_user.id
    await query.answer("Searching")
    # database check for resume
    async with SessionLocal() as session:
        await rq.update_my_jobs_city_search(session, user_id, True)
    updated_keyboard = await nav.create_blank_keyboard("Search 🔎")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    await query.message.answer("Searching...", reply_markup=nav.nextMenu)
    await state.set_state(Jobs.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        job = await rq.get_next_job_by_id_with_city(session, user.jobs_search_id_list, user.city, user_id)
        if job:
            summary = await post_summary(job)
            await query.message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
            await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
        elif job is None:
            await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("Would you like to search job options outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
        else:
            await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  

@job_router.callback_query(nav.MenuCallback.filter(F.menu == "jobs_go_search_beyond"))
async def search_beyond_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Searching beyond")
    async with SessionLocal() as session:
        await rq.update_my_jobs_city_search(session, user_id, False)
    updated_keyboard = await nav.create_blank_keyboard("Search beyond city 🔎")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    await query.message.answer("Searching beyond...", reply_markup=nav.nextMenu)
    await state.set_state(Jobs.searching)
    async with SessionLocal() as session:
        user = await rq.get_user(session, user_id)
        job = await rq.get_next_job_by_id_without_city(session, user.jobs_search_id_list, user.city, user_id)
        if job:
            summary = await post_summary(job)
            await query.message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
            await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
        else:
            await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  



# ---NEW POST---
@job_router.callback_query(nav.JobsCallback.filter(F.action == "post_ad"))
async def new_job_by_query(query: CallbackQuery, state: FSMContext):
    await query.answer("Creating new ad")
    updated_keyboard = await nav.create_blank_keyboard("Post an ad 📰")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    await query.message.answer("Creating your ad...\
                         \nMind that you can always \nGo /back or /cancel the process")
    await state.set_state(Job.title)
    await query.message.answer("Type the title for your ad:")
    await set_back_commands(id=query.from_user.id)



# --- MY POSTS ---
@job_router.callback_query(nav.MenuCallback.filter(F.menu == "my_job_ads"))
@job_router.callback_query(nav.JobsCallback.filter(F.action == "my_job_ads"))
async def my_job_posts_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    await query.answer("My job ads")
    # print("CALLBACK DATA", callback_data) 
    # print("CALLBACK DATA", callback_data.model_dump_json()) 
    # print("CALLBACK DATA", callback_data.model_dump()) 
    # print("CALLBACK DATA", type(callback_data))
    # print("menu" in callback_data.model_dump())
    # print("menu" in callback_data.model_dump().keys())
    if "menu" in callback_data.model_dump():
        updated_keyboard = await nav.create_blank_keyboard("View my job ads 🧾")
    else:
        updated_keyboard = await nav.create_blank_keyboard("Back")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
        
    # make a database request
    # and further manipulations
    async with SessionLocal() as session:
        my_jobs = await rq.get_user_jobs(session, query.from_user.id)
        for job in my_jobs:
            print(job.title, job.id)
        if my_jobs:            
            keyboard = await nav.create_jobs_keyboard(my_jobs)
            # title = await query.message.answer("--- Posts Manager ---", reply_markup=ReplyKeyboardRemove()) if has_title else None
            await query.message.answer("My job ads", reply_markup=keyboard) 
            # if edit_message else await message.answer("My Posts", reply_markup=keyboard)
            # if title:
            #     await title.delete()
        else:
            # create redirecting
            answer = await query.message.answer("You have no job ads")
            await start_jobs(answer, state)
async def my_job_posts_by_message(message: Message, state: FSMContext, user_id: int = 0):
    updated_keyboard = await nav.create_blank_keyboard("Deleted")
    await message.edit_reply_markup(reply_markup=updated_keyboard)
    # await message.answer("Hello")
    # make a database request
    # and further manipulations
    async with SessionLocal() as session:
        my_jobs = await rq.get_user_jobs(session, user_id or message.from_user.id)
        for job in my_jobs:
            print(job.title, job.id)
        if my_jobs:
            keyboard = await nav.create_jobs_keyboard(my_jobs)
            # title = await message.answer("--- Posts Manager ---", reply_markup=ReplyKeyboardRemove()) if has_title else None
            await message.answer("My Posts", reply_markup=keyboard)
            # if title:
            #     await title.delete()
        else:
            answer = await message.answer("You have no job ads")
            await start_jobs(answer, state)

@job_router.callback_query(nav.JobsCallback.filter(F.action == "manage"))
async def handle_job_list_by_query(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
    await query.answer("Post")
    job_id, additional = int(callback_data.id), callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard(f"{additional}")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    # await query.message.answer(query.chat_instance)
    # Query the job
    async with SessionLocal() as session:
        my_job = await rq.get_job_by_id(session, job_id)
        if my_job:
            keyboard = await nav.create_single_job_keyboard(my_job.id, my_job.title)
            summary = await post_summary(my_job)
            await query.message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=keyboard) 
        else:
            await query.message.answer("You do not have any posts")
async def handle_job_list_by_message(message: Message, callback_data: nav.JobsCallback, state: FSMContext, update_keyboard: bool = False):
    job_id, additional = int(callback_data.id), callback_data.additional
    if update_keyboard:
        updated_keyboard = await nav.create_blank_keyboard(f"{additional}")
        await message.edit_reply_markup(reply_markup=updated_keyboard)
    # await query.message.answer(query.chat_instance)
    # Query the job
    async with SessionLocal() as session:
        my_job = await rq.get_job_by_id(session, job_id)
        if my_job:
            # await query.answer("Post")
            keyboard = await nav.create_single_job_keyboard(my_job.id, my_job.title)
            summary = await post_summary(my_job)
            await message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=keyboard) 
        else:
            await message.answer("You do not have any posts")           



@job_router.callback_query(nav.JobsCallback.filter(F.action == "delete"))
async def handle_job_delete_by_query(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
    job_id = int(callback_data.id)
    additional = callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard(f"{additional}")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    print("ID", job_id)
    # Delete the job
    async with SessionLocal() as session:
        deleted_job = await rq.delete_job_by_id(session, job_id)
        if deleted_job:
            await query.answer("Deleted")
            # await query.message.answer("Job post successfully deleted")
            # await query.message.edit_reply_markup(ReplyKeyboardRemove())
            await my_job_posts_by_message(query.message, state, user_id=query.from_user.id)
        else:
            await query.answer("Error")

### FINISHED CHANGING

# FINISH APPLICANTS CHECK
@job_router.callback_query(nav.JobsCallback.filter(F.action == "check_applicants"))
async def handle_job_check_applicants_by_query(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
    # user_id = query.from_user.id
    job_id = int(callback_data.id)
    additional = callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard("🖱️ Check applicants")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    async with SessionLocal() as session:
        job_applicants = await rq.get_applicants_by_job_id(session, job_id)
        if job_applicants:
            await query.answer("Applicants")
            keyboard = await nav.create_job_applicants_keyboard(job_applicants, job_id)
            # summary = await post_summary(my_job)
            await query.message.answer(text="Applicants", parse_mode=ParseMode.HTML, reply_markup=keyboard) 
        else:
            callback_data = nav.JobsCallback(id=str(job_id), action="list", additional="🖱️ Check applicants")
            answer = await query.message.answer("There are no applicants yet")
            await handle_job_list_by_message(answer, callback_data, state, True)       


@job_router.callback_query(nav.JobsCallback.filter(F.action == "edit"))
async def handle_job_edit_by_query(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
    await query.answer("Edit")
    job_id = int(callback_data.id)
    # additional = callback_data.additional
    updated_keyboard = await nav.create_blank_keyboard("✏️ Edit")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    keyboard = await nav.create_edit_job_keyboard(job_id)
    await query.message.answer("What do you want to edit?", reply_markup=keyboard)
@job_router.callback_query(nav.JobsCallback.filter())
async def handle_job_field_edit_by_query(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
    job_id = int(callback_data.id)
    await state.set_state(JobEdit.job_id)
    await state.update_data(job_id=job_id)
    await state.set_state(JobEdit.chat_instance)
    await state.update_data(chat_instance=query.chat_instance)
    await query.answer(f"{callback_data.action.capitalize()}")
    match callback_data.action:
        case "title":
            updated_keyboard = await nav.create_blank_keyboard("Title")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(JobEdit.title)
            await query.message.answer("Provide new title")
        case "description":
            updated_keyboard = await nav.create_blank_keyboard("Description")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(JobEdit.description)
            await query.message.answer("Provide new description")
        case "skills":
            updated_keyboard = await nav.create_blank_keyboard("Skills")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(JobEdit.skills)
            await query.message.answer("Provide new skills")
        case "city":
            updated_keyboard = await nav.create_blank_keyboard("City")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(JobEdit.location)
            await query.message.answer("Provide new city")
        case "address":
            updated_keyboard = await nav.create_blank_keyboard("Address")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(JobEdit.address)
            await query.message.answer("Provide new address")
@job_router.message(JobEdit.title, F.text)
@job_router.message(JobEdit.description, F.text)
@job_router.message(JobEdit.skills, F.text)
@job_router.message(JobEdit.location, F.location)
@job_router.message(JobEdit.location, F.text)
@job_router.message(JobEdit.address, F.location)
@job_router.message(JobEdit.address, F.text)
async def handle_job_field_update_callback(message: Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    job_id = data["job_id"]
    callback_data = nav.JobsCallback(id=str(job_id), action="list", additional="")
    match current_state:
        case JobEdit.title.state:
            print("JOB ID", job_id)
            print("Current State", current_state)
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_job_by_id(session, job_id, JobModel.title, message.text) 
                if updated:
                    await message.answer("Title successfully updated")
                    await handle_job_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case JobEdit.description.state:
            async with SessionLocal() as session:
                updated = await rq.update_job_by_id(session, job_id, JobModel.description, message.text) 
                if updated:
                    await message.answer("Description successfully updated")
                    await handle_job_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case JobEdit.skills.state:
            async with SessionLocal() as session:
                updated = await rq.update_job_by_id(session, job_id, JobModel.skills, message.text) 
                if updated:
                    await message.answer("Skills successfully updated")
                    await handle_job_list_by_message(message, callback_data, state)
                else: 
                    await message.answer("Error")
        case JobEdit.location.state:
            if message.location:
                user_location = location.get_location(message.location.latitude, message.location.longitude)
                print(user_location)
                address = user_location[1]
                async with SessionLocal() as session:
                    updated = await rq.update_job_by_id(session, job_id, JobModel.city, address)
                    if updated:
                        await message.answer("City successfully updated")
                        await handle_job_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
            else:
                async with SessionLocal() as session:
                    updated = await rq.update_job_by_id(session, job_id, JobModel.city, message.text) 
                    if updated:
                        await message.answer("City successfully updated")
                        await handle_job_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
        case JobEdit.address.state:
            if message.location:
                user_location = location.get_location(message.location.latitude, message.location.longitude)
                print(user_location)
                address = user_location[0]
                async with SessionLocal() as session:
                    updated = await rq.update_job_by_id(session, job_id, JobModel.address, address)
                    if updated:
                        await message.answer("Address successfully updated")
                        await handle_job_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")
            else:
                async with SessionLocal() as session:
                    updated = await rq.update_job_by_id(session, job_id, JobModel.address, message.text) 
                    if updated:
                        await message.answer("Address successfully updated")
                        await handle_job_list_by_message(message, callback_data, state)
                    else: 
                        await message.answer("Error")




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
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.jobsReplyChoiceMenu.as_markup())


async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
    title = data["title"]
    description = data["description"]
    skills = data["skills"]
    location = data["location"]
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
        job = await search_funcitons_map[user.jobs_city_search](session, user.jobs_search_id_list, user.city, user_id)
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



@job_router.callback_query(nav.BlankCallback.filter())
async def handle_blank(query: CallbackQuery, callback_data: nav.BlankCallback):
    text = callback_data.text
    await query.answer(f"{text}")
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

