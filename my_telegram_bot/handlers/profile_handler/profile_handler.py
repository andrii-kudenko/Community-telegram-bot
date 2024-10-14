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

from . import profile_markup as nav
from markups import markups
from utils import location
from bot_info import set_back_commands, set_default_commands
from database import profile_requests as rq
from database.models import SessionLocal
from database.models import Resume as ResumeModel

class ResumeBuilder(StatesGroup):
    full_name = State()
    email_address = State()
    phone_number = State()
    location = State()
    work_experience = State()
    degree_description = State()
    skills = State()
    languages = State()
    additional_information = State()

profile_router = Router(name=__name__)

# --- COMMANDS ---
@profile_router.message(Command("profile", prefix=("!/")))
async def start_profile(message: Message, state: FSMContext):
    # await state.set_state(Jobs.choice)
    await message.answer("Hi there! Choose the action:", reply_markup=nav.choiceMenu.as_markup())


@profile_router.callback_query(nav.MenuCallback.filter(F.menu == "start_profile"))
@profile_router.callback_query(nav.ResumeCallback.filter(F.action == "start_profile"))
async def start_profile_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    await query.answer("Profile")
    if "menu" in callback_data.model_dump():
        updated_keyboard = await nav.create_blank_keyboard("Profile 👤")
    else:
        updated_keyboard = await nav.create_blank_keyboard("Back")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    # await query.answer("Jobs")
    # await state.set_state(Jobs.choice)
    # await query.message.delete()
    await query.message.answer("Hi there! Choose the action:", reply_markup=nav.choiceMenu.as_markup())


@profile_router.callback_query(nav.MenuCallback.filter(F.menu == "my_resume_editor"))
@profile_router.callback_query(nav.ResumeCallback.filter(F.action == "my_resume_editor"))
async def my_resume_editor_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("My Resume")
    if "menu" in callback_data.model_dump():
        updated_keyboard = await nav.create_blank_keyboard("Resume Editor")
    elif "action" in callback_data.model_dump():
        updated_keyboard = await nav.create_blank_keyboard("Back")
    else:
        updated_keyboard = None # to be added
        # updated_keyboard = await nav.create_blank_keyboard("Deleted") # to be added
    await query.message.edit_reply_markup(reply_markup=updated_keyboard) if updated_keyboard else None
    # await query.answer("My Resume")
    # await state.set_state(Jobs.choice)
    # await query.message.delete()
    # DB call for resume
    async with SessionLocal() as session:
        my_resume = await rq.get_my_resume(session, user_id)
        if my_resume:
            keyboard = await nav.create_my_resume_keyboard(my_resume)
            # summary = await resume_summary(my_resume)
            await query.message.answer(text="Resume editor", reply_markup=keyboard) 
        else:
            await query.message.answer("You do not have a resume yet, do you want to create one?", reply_markup=nav.createResumeMenu.as_markup())
    # await query.message.edit_text("Resume:", reply_markup=nav.choiceMenu.as_markup())
async def my_resume_editor_by_messsage(message: Message, state: FSMContext):
    # user_id = message.from_user.id
    print("MESSAGE", message)
    async with SessionLocal() as session:
        my_resume = await rq.get_my_resume(session, message.from_user.id)
        if my_resume:
            keyboard = await nav.create_my_resume_keyboard(my_resume)
            # summary = await resume_summary(my_resume)
            await message.answer(text="Resume editor", reply_markup=keyboard) 
        else:
            await message.answer("Error")

@profile_router.callback_query(nav.ResumeCallback.filter(F.action == "create_resume"))
async def create_resume(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Resume Creation")
    updated_keyboard = await nav.create_blank_keyboard("Created")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    async with SessionLocal() as session:
        created_resume = await rq.create_resume(session, user_id)
        if created_resume:
            await query.message.answer("Resume created")
            callback_data = nav.BlankCallback(text="Deleted")
            await my_resume_editor_by_query(query, callback_data, state)
        else:
            await query.message.answer("Error")
            callback_data = nav.BlankCallback(text="Error")
            await my_resume_editor_by_query(query, callback_data, state)


@profile_router.callback_query(nav.ResumeCallback.filter(F.action == "my_resume"))
async def my_resume(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer("Resume")
    updated_keyboard = await nav.create_blank_keyboard("View my resume")
    await query.message.edit_reply_markup(reply_markup=updated_keyboard)
    async with SessionLocal() as session:
        my_resume = await rq.get_my_resume(session, user_id)
        print("RESUME ", my_resume.full_name, my_resume.email_address, my_resume.additional_information)
        if not my_resume.full_name or not my_resume.email_address or not my_resume.additional_information:
            await query.message.answer("Resume is incomplete. Try adding required* information to complete your resume")
            callback_data = nav.BlankCallback(text="Error")
            await my_resume_editor_by_query(query, callback_data, state)
        elif my_resume:
            summary = await resume_summary(my_resume)
            await query.message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.myResumeMenu.as_markup())
        else:
            await query.message.answer("Error")


@profile_router.callback_query(nav.ResumeCallback.filter())
async def handle_job_field_edit_callback(query: CallbackQuery, callback_data: nav.ResumeCallback, state: FSMContext):
    user_id = query.from_user.id
    
    # job_id = int(callback_data.id)
    # await state.set_state(JobEdit.job_id)
    # await state.update_data(job_id=job_id)
    # await state.set_state(JobEdit.chat_instance)
    # await state.update_data(chat_instance=query.chat_instance)
    await query.answer(f"{callback_data.action.capitalize()}")
    match callback_data.action:
        case "full_name":
            updated_keyboard = await nav.create_blank_keyboard("full name")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.full_name)
            await query.message.answer("Provide full name")
        case "email_address":
            updated_keyboard = await nav.create_blank_keyboard("email address")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.email_address)
            await query.message.answer("Provide email address")
        case "phone_number":
            updated_keyboard = await nav.create_blank_keyboard("phone number")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.phone_number)
            await query.message.answer("Provide phone number")
        case "location":
            updated_keyboard = await nav.create_blank_keyboard("location")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.location)
            await query.message.answer("Provide location")
        case "work_experience":
            updated_keyboard = await nav.create_blank_keyboard("work experience")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.work_experience)
            await query.message.answer("Provide work experience")
        case "degree_description":
            updated_keyboard = await nav.create_blank_keyboard("degree description")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.degree_description)
            await query.message.answer("Provide degree description")
        case "skills":
            updated_keyboard = await nav.create_blank_keyboard("skills")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.skills)
            await query.message.answer("Provide skills")
        case "languages":
            updated_keyboard = await nav.create_blank_keyboard("languages")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.languages)
            await query.message.answer("Provide languages")
        case "additional_information":
            updated_keyboard = await nav.create_blank_keyboard("additional information")
            await query.message.edit_reply_markup(reply_markup=updated_keyboard)
            await state.set_state(ResumeBuilder.additional_information)
            await query.message.answer("Provide information about you")

@profile_router.message(ResumeBuilder.full_name, F.text)
@profile_router.message(ResumeBuilder.email_address, F.text)
@profile_router.message(ResumeBuilder.phone_number, F.text)
@profile_router.message(ResumeBuilder.location, F.location)
@profile_router.message(ResumeBuilder.location, F.text)
@profile_router.message(ResumeBuilder.work_experience, F.text)
@profile_router.message(ResumeBuilder.degree_description, F.location)
@profile_router.message(ResumeBuilder.skills, F.text)
@profile_router.message(ResumeBuilder.languages, F.text)
@profile_router.message(ResumeBuilder.additional_information, F.text)
async def handle_resume_field_update_callback(message: Message, state: FSMContext):
    user_id = message.from_user.id
    current_state = await state.get_state()
    match current_state:
        case ResumeBuilder.full_name.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.full_name, message.text) 
                if updated:
                    await message.answer("Full name updated")
                    await my_resume_editor_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.email_address.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.email_address, message.text) 
                if updated:
                    await message.answer("Email address updated")
                    await my_resume_editor_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.phone_number.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.phone_number, message.text) 
                if updated:
                    await message.answer("Phone number updated")
                    await my_resume_editor_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.location.state:
            # DB query to edit field
            if message.location:
                user_location = location.get_location(message.location.latitude, message.location.longitude)
                print(user_location)
                address = user_location[1]
                async with SessionLocal() as session:
                    updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.city, address) 
                    if updated:
                        await message.answer("Location updated")
                        await my_resume_editor_by_messsage(message, state)
                    else: 
                        await message.answer("Error")
            else:
                async with SessionLocal() as session:
                    updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.city, message.text) 
                    if updated:
                        await message.answer("Location updated")
                        await my_resume_editor_by_messsage(message, state)
                    else: 
                        await message.answer("Error")
        case ResumeBuilder.work_experience.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.work_experience, message.text) 
                if updated:
                    await message.answer("Work experience updated")
                    await my_resume_editor_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.degree_description.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.degree_description, message.text) 
                if updated:
                    await message.answer("Degree description updated")
                    await my_resume_editor_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.skills.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.skills, message.text) 
                if updated:
                    await message.answer("Skills updated")
                    await my_resume_editor_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.languages.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.languages, message.text) 
                if updated:
                    await message.answer("Languages updated")
                    await my_resume_editor_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.additional_information.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.additional_information, message.text) 
                if updated:
                    await message.answer("Additional information updated")
                    await my_resume_editor_by_messsage(message, state)
                else: 
                    await message.answer("Error")

    # await message.answer("Full name updated")
    # await message.answer("Email updated")
    # await message.answer("Phone number updated")
    # await message.answer("Location updated")
    # await message.answer("Work experience updated")
    # await message.answer("Degree description updated")
    # await message.answer("Skills updated")
    # await message.answer("Languages updated")
    # await message.answer("Additional information updated")


# --- HELPER FUNCTIONS ---
async def resume_summary(resume: ResumeModel): # use ParseMode.HTML (parse_mode=ParseMode.HTML), need to work on styling 
    if resume.skills:
        resume_skills: str = resume.skills
        skills_list: list = resume_skills.split(',')
        skills_formatted = "\n".join([f"- {skill.strip().capitalize()}" for skill in skills_list])

    summary = ""

    attributes = [ 'full_name',
        'email_address', 'additional_information',
        'phone_number', 'location', 'work_experience', 
        'degree_description', 'skills', 'languages'
    ]
    attr_dict = {
    'full_name': "Name",
    'additional_information': "About",
    'email_address': "Email", 
    'phone_number': "Phone", 
    'location': "Location", 
    'work_experience': "Experience", 
    'degree_description': "Degrees",
    'skills': "Skills", 
    'languages': "Languages", 
}
    for attr in attributes:
        value = getattr(resume, attr, None)
        if value:
            summary += f"<b>{attr_dict[attr]}:</b> {value}\n"

    # summary = (
    #     f"Full name: <u>{resume.full_name}</u>\n" if resume.full_name else ""
    #     f"About: {resume.additional_information}\n" if resume.additional_information else ""
    #     f"Email: {resume.email_address}\n" if resume.email_address else ""
    #     f"Phone: {resume.phone_number}\n" if resume.phone_number else ""
    #     f"Work experience: {resume.work_experience}\n" if resume.work_experience else ""
    #     f"Degree description: {resume.degree_description}\n" if resume.degree_description else ""
    #     f"Languages: {resume.languages}\n" if resume.languages else ""
    #     f"Skills: \n{skills_formatted}\n" if resume.skills else ""
    #     f"Location: {resume.location}\n" if resume.location else ""
    # )
    return summary