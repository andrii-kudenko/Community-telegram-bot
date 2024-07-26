from typing import Any, Dict
import logging

from aiogram import Router, F, html
from aiogram.utils import markdown
from aiogram.utils.markdown import bold, italic, text, code, pre
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from . import jobs_markup as nav
from utils import location
from bot_info import set_back_commands, set_default_commands

job_router = Router(name=__name__)

class Jobs(StatesGroup):
    choice = State()
    searching = State()

class Job(StatesGroup):
    title = State()
    description = State()
    skills = State()
    location = State()

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

@job_router.message(Jobs.choice, F.text == "Search 🔎")
async def search(message: Message, state: FSMContext):
    # await message.answer("Searching...")
    job_title = "Software Developer"
    job_description = "We are looking for a skilled software developer to join our team. The ideal candidate will have experience in developing scalable web applications and a strong understanding of software development principles."
    job_skills = ["Python", "JavaScript", "SQL", "HTML/CSS", "Git", "Agile methodology"]
    job_location = "Remote or On-site in San Francisco, CA"

    skills_formatted = "\n".join([f"- {skill}" for skill in job_skills])

    summary = (
        f"<b>{job_title}</b>\n\n"
        f"<code>{job_description}</code>\n\n"
        "Skills required:\n"
        f"{skills_formatted}\n\n"
        f"<i>{job_location}</i>"
    )

    await message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove()) 
    await state.set_state(Jobs.searching)
@job_router.message(Jobs.choice, F.text == "Post an ad 📰")
async def job(message: Message, state: FSMContext):
    await message.answer("Creating your ad...\
                         \nMind that you can always \nGo /back or /cancel the process")
    await state.set_state(Job.title)
    await message.answer("Type the title for your ad:", reply_markup=ReplyKeyboardRemove())
    await set_back_commands(id=message.from_user.id)
@job_router.message(Jobs.choice)
async def choice_invalid(message: Message):
    await message.answer("I don't understand you. Please choose your action or Go /home")


# ---POST CREATION---
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
@job_router.message(Job.location, F.text)
async def job_location(message: Message, state: FSMContext):
    if message.location:
        user_location = location.get_location(message.location.latitude, message.location.longitude)
        print(user_location)
        data = await state.update_data(location=user_location[1])
    else:
        data = await state.update_data(location=message.text)     
    await state.clear()

    await show_summary(message=message, data=data)

    # Database call to add a post to user

    await state.set_state(Jobs.choice)
    await message.answer("Good, your ad is successfully posted!", reply_markup=nav.jobsReplyChoiceMenu)
    await set_default_commands(id=message.from_user.id)
async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
    title = data["title"]
    description = data["description"]
    skills = data["skills"]
    location = data["location"]
    summary = text(
        text(f"{html.underline('Job overview:\n')}"),
        text(f"{html.bold('Title:')} {title}\n"),
        text(f"{html.bold('Description:')} {html.italic(description)}\n"),
        text(f"{html.bold('Skills (required):')} {html.code(skills)}"),
        text(f"{html.blockquote(location)}"),
    )
    summary = markdown.text(
                markdown.hbold(f'{title}\n'),
                markdown.hcode(f'{description}\n'),
                markdown.text('Skills required:'),
                markdown.hitalic(f'{skills}'),
                markdown.hblockquote(f'{location}')
            )
    await message.answer(text=summary, reply_markup=ReplyKeyboardRemove())

# @job_router.message()
# async def invalid_input(message: Message):
#      await message.answer("Please, provide a valid answer jobs")

async def post_summary(): # use ParseMode.HTML (parse_mode=ParseMode.HTML)
    skills_formatted = "\n".join([f"- {skill}" for skill in job_skills])

    summary = (
        f"<b>{job_title}</b>\n\n"
        f"<code>{job_description}</code>\n\n"
        "Skills required:\n"
        f"{skills_formatted}\n\n"
        f"<i>{job_location}</i>"
    )
    return summary