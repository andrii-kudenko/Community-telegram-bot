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
from database import jobs_requests as rq
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


@profile_router.callback_query(nav.MenuCallback.filter(F.menu == "leave"))
async def start_jobs_by_query(query: CallbackQuery, state: FSMContext):
    # await query.answer("Jobs")
    # await state.set_state(Jobs.choice)
    # await query.message.delete()
    await query.message.answer("Hi there! Choose the action:", reply_markup=nav.choiceMenu.as_markup())


@profile_router.callback_query(nav.MenuCallback.filter(F.menu == "my_resume"))
async def my_resume_by_query(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    # await query.answer("My Resume")
    # await state.set_state(Jobs.choice)
    # await query.message.delete()
    # DB call for resume
    async with SessionLocal() as session:
        my_resume = await rq.get_my_resume(session, user_id)
        if my_resume:
            await query.answer("My Resume")
            keyboard = await nav.create_my_resume_keyboard(my_resume)
            summary = await resume_summary(my_resume)
            await query.message.edit_text(text=summary, parse_mode=ParseMode.HTML, reply_markup=keyboard) 
        else:
            await query.message.answer("You do not have resume")
    # await query.message.edit_text("Resume:", reply_markup=nav.choiceMenu.as_markup())
async def my_resume_by_messsage(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with SessionLocal() as session:
        my_resume = await rq.get_my_resume(session, user_id)
        if my_resume:
            keyboard = await nav.create_my_resume_keyboard(my_resume)
            summary = await resume_summary(my_resume)
            await message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=keyboard) 
        else:
            await message.answer("You do not have resume")


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
            await state.set_state(ResumeBuilder.full_name)
            await query.message.answer("Provide new title")
        case "email_address":
            await state.set_state(ResumeBuilder.email_address)
            await query.message.edit_text("Provide new description")
        case "phone_number":
            await state.set_state(ResumeBuilder.phone_number)
            await query.message.answer("Provide new skills")
        case "location":
            await state.set_state(ResumeBuilder.location)
            await query.message.answer("Provide new city")
        case "work_experience":
            await state.set_state(ResumeBuilder.work_experience)
            await query.message.answer("Provide new address")
        case "degree_description":
            await state.set_state(ResumeBuilder.degree_description)
            await query.message.answer("Provide new address")
        case "skills":
            await state.set_state(ResumeBuilder.skills)
            await query.message.answer("Provide new address")
        case "languages":
            await state.set_state(ResumeBuilder.languages)
            await query.message.answer("Provide new address")
        case "additional_information":
            await state.set_state(ResumeBuilder.additional_information)
            await query.message.answer("Provide new address")

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
                    await my_resume_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.email_address.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.email_address, message.text) 
                if updated:
                    await message.answer("Email address updated")
                    await my_resume_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.phone_number.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.phone_number, message.text) 
                if updated:
                    await message.answer("Phone number updated")
                    await my_resume_by_messsage(message, state)
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
                        await my_resume_by_messsage(message, state)
                    else: 
                        await message.answer("Error")
            else:
                async with SessionLocal() as session:
                    updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.city, message.text) 
                    if updated:
                        await message.answer("Location updated")
                        await my_resume_by_messsage(message, state)
                    else: 
                        await message.answer("Error")
        case ResumeBuilder.work_experience.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.work_experience, message.text) 
                if updated:
                    await message.answer("Work experience updated")
                    await my_resume_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.degree_description.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.degree_description, message.text) 
                if updated:
                    await message.answer("Degree description updated")
                    await my_resume_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.skills.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.skills, message.text) 
                if updated:
                    await message.answer("Skills updated")
                    await my_resume_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.languages.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.languages, message.text) 
                if updated:
                    await message.answer("Languages updated")
                    await my_resume_by_messsage(message, state)
                else: 
                    await message.answer("Error")
        case ResumeBuilder.additional_information.state:
            # DB query to edit field
            async with SessionLocal() as session:
                updated = await rq.update_resume_by_user_id(session, user_id, ResumeModel.additional_information, message.text) 
                if updated:
                    await message.answer("Additional information updated")
                    await my_resume_by_messsage(message, state)
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