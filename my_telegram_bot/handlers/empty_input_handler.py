from aiogram import Router
from aiogram.types import Message 
empty_router = Router(name=__name__)
# @empty_router.message()
# async def catch_empty(message: Message):
#     await message.answer("Please, provide a valid answer empty")



# ###


# # --- COMMANDS ---
# @job_router.message(Command("jobs", prefix=("!/")))
# async def start_jobs(message: Message, state: FSMContext):
#     await state.set_state(Jobs.choice)
#     await message.answer("Hi there! Choose the action:", reply_markup=nav.jobsReplyChoiceMenu)
# @job_router.callback_query(nav.JobsCallback.filter(F.action == "leave"))
# async def start_jobs_by_query(query: CallbackQuery, state: FSMContext):
#     await query.answer("Jobs")
#     await state.set_state(Jobs.choice)
#     await query.message.delete()
#     await query.message.answer("Hi there! Choose the action:", reply_markup=nav.jobsReplyChoiceMenu)

# @job_router.message(Job.title, Command("cancel", prefix=("!/")))
# @job_router.message(Job.description, Command("cancel", prefix=("!/")))
# @job_router.message(Job.skills, Command("cancel", prefix=("!/")))
# @job_router.message(Job.location, Command("cancel", prefix=("!/")))
# async def cancel_handler(message: Message, state: FSMContext) -> None:
#     current_state = await state.get_state()
#     if current_state is None:
#         return

#     logging.info("Cancelling state %r", current_state)
#     await state.set_state(Jobs.choice)
#     await message.answer(
#         "Cancelled",
#         reply_markup=nav.jobsReplyChoiceMenu,
#     )
#     await set_default_commands(id=message.from_user.id)

# @job_router.message(Job.title, Command("back", prefix=("!/")))
# @job_router.message(Job.description, Command("back", prefix=("!/")))
# @job_router.message(Job.skills, Command("back", prefix=("!/")))
# @job_router.message(Job.location, Command("back", prefix=("!/")))
# async def back_handler(message: Message, state: FSMContext) -> None:
#     current_state = await state.get_state()
#     if current_state == Job.title:
#             await state.set_state(Jobs.choice)
#             await message.answer("Choose action:", reply_markup=nav.jobsReplyChoiceMenu)
#     elif current_state == Job.description:
#             await state.set_state(Job.title)
#             await message.answer("Send me new title")
#     elif current_state == Job.skills:
#             await state.set_state(Job.description)
#             await message.answer("Send me new description")
#     elif current_state == Job.location:
#             await state.set_state(Job.skills)
#             await message.answer("Send me new skills")



# # --- SEARCH ---
# @job_router.message(Jobs.choice, F.text == "Search 🔎")
# async def search_by_message(message: Message, state: FSMContext): 
#     user_id = message.from_user.id
#     # database check for resume
#     async with SessionLocal() as session:
#         await rq.update_my_jobs_city_search(session, user_id, True)
#     await message.answer("Searching...", reply_markup=nav.nextMenu)
#     await state.set_state(Jobs.searching)
#     async with SessionLocal() as session:
#         user = await rq.get_user(session, user_id)
#         job = await rq.get_next_job_by_id_with_city(session, user.jobs_search_id_list, user.city, user_id)
#         if job:
#             summary = await post_summary(job)
#             await message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
#             await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
#         elif job is None:
#             await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
#             await message.answer("Would you like to search job options outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
#         else:
#             await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
#             await message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  
# # @job_router.callback_query(nav.MenuCallback.filter(F.menu == "go_search"))
# # async def search_by_query(query: CallbackQuery, state: FSMContext):
# #     await query.answer("Searching")
# #     user_id = query.from_user.id
# #     # database check for resume
# #     await query.message.answer("Searching...", reply_markup=nav.nextMenu)
# #     await state.set_state(Jobs.searching)
# #     async with SessionLocal() as session:
# #         user = await rq.get_user(session, user_id)
# #         job = await rq.get_next_job_by_id_with_city(session, user.jobs_search_id_list, user.city)
# #         if job: 
# #             summary = await post_summary(job)
# #             await query.message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
# #             await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
# #         if job is None:
# #             await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
# #             await query.message.answer("You can come later to see new available job vacations", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
# #         else:
# #             await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
# #             await query.message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  
# @job_router.callback_query(nav.MenuCallback.filter(F.menu == "jobs_go_search_beyond"))
# async def search_beyond_by_query(query: CallbackQuery, state: FSMContext):
#     await query.answer("Searching outside")
#     user_id = query.from_user.id
#     async with SessionLocal() as session:
#         await rq.update_my_jobs_city_search(session, user_id, False)
#     await query.message.answer("Searching...", reply_markup=nav.nextMenu)
#     await state.set_state(Jobs.searching)
#     async with SessionLocal() as session:
#         user = await rq.get_user(session, user_id)
#         job = await rq.get_next_job_by_id_without_city(session, user.jobs_search_id_list, user.city, user_id)
#         if job:
#             summary = await post_summary(job)
#             await query.message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
#             await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
#         else:
#             await query.message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
#             await query.message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  



# # --- MY POSTS ---
# @job_router.message(Jobs.choice, F.text == "View my job ads 🧾")
# async def my_job_posts_by_message(message: Message, state: FSMContext, user_id: int = 0, has_title: bool = True, edit_message: bool = False):
#     # await message.answer("Hello")
#     # make a database request
#     # and further manipulations
#     async with SessionLocal() as session:
#         my_jobs = await rq.get_user_jobs(session, user_id or message.from_user.id)
#         for job in my_jobs:
#             print(job.title, job.id)
#         if my_jobs:
#             keyboard = await nav.create_jobs_keyboard(my_jobs)
#             title = await message.answer("--- Posts Manager ---", reply_markup=ReplyKeyboardRemove()) if has_title else None
#             await message.edit_text("My Posts", reply_markup=keyboard) if edit_message else await message.answer("My Posts", reply_markup=keyboard)
#             if title:
#                 await title.delete()
#         # else:
#         #     await message.answer("No posts")
# @job_router.callback_query(nav.MenuCallback.filter(F.menu == "my_job_ads"))
# async def my_job_posts_by_query(query: CallbackQuery, state: FSMContext):
#     # make a database request
#     # and further manipulations
#     async with SessionLocal() as session:
#         my_jobs = await rq.get_user_jobs(session, query.from_user.id)
#         for job in my_jobs:
#             print(job.title, job.id)
#         if my_jobs:
#             keyboard = await nav.create_jobs_keyboard(my_jobs)
#             # title = await query.message.answer("--- Posts Manager ---", reply_markup=ReplyKeyboardRemove()) if has_title else None
#             await query.message.edit_text("My job ads", reply_markup=keyboard) 
#             # if edit_message else await message.answer("My Posts", reply_markup=keyboard)
#             # if title:
#             #     await title.delete()
#         else:
#             await query.message.answer("You have no job ads")
#     # await query.message.answer("My posts")
# @job_router.callback_query(nav.JobsCallback.filter(F.action == "manage"))
# async def handle_job_list_callback(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
#     job_id = int(callback_data.id)
#     # await query.message.answer(query.chat_instance)
#     # Query the job
#     async with SessionLocal() as session:
#         my_job = await rq.get_job_by_id(session, job_id)
#         if my_job:
#             await query.answer("Post")
#             keyboard = await nav.create_single_job_keyboard(my_job.id)
#             summary = await post_summary(my_job)
#             await query.message.edit_text(text=summary, parse_mode=ParseMode.HTML, reply_markup=keyboard) 
#         else:
#             await query.message.answer("You do not have any posts")
# async def handle_job_list_by_message(message: Message, callback_data: nav.JobsCallback, state: FSMContext):
#     job_id = int(callback_data.id)
#     # await query.message.answer(query.chat_instance)
#     # Query the job
#     async with SessionLocal() as session:
#         my_job = await rq.get_job_by_id(session, job_id)
#         if my_job:
#             # await query.answer("Post")
#             keyboard = await nav.create_single_job_keyboard(my_job.id)
#             summary = await post_summary(my_job)
#             await message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=keyboard) 
#         else:
#             await message.answer("You do not have any posts")            
# @job_router.callback_query(nav.JobsCallback.filter(F.action == "back"))
# async def handle_job_back_callback(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
#     job_id = int(callback_data.id)
#     print("ID", job_id)
#     await query.answer("Back")
#     await query.message.edit_text("Canceled")
#     await my_job_posts_by_message(query.message, state, user_id=query.from_user.id, has_title=False, edit_message=True)
# @job_router.callback_query(nav.JobsCallback.filter(F.action == "delete"))
# async def handle_job_delete_callback(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
#     job_id = int(callback_data.id)
#     print("ID", job_id)
#     # Delete the job
#     async with SessionLocal() as session:
#         deleted_job = await rq.delete_job_by_id(session, job_id)
#         if deleted_job:
#             await query.answer("Deleted")
#             await query.message.edit_text("Job post successfully deleted")
#             # await query.message.edit_reply_markup(ReplyKeyboardRemove())
#             await my_job_posts_by_message(query.message, state, user_id=query.from_user.id, has_title=False)
#         else:
#             await query.answer("Error")



# # FINISH APPLICANTS CHECK
# @job_router.callback_query(nav.JobsCallback.filter(F.action == "check_applicants"))
# async def handle_job_check_applicants_callback(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
#     # user_id = query.from_user.id
#     job_id = int(callback_data.id)
#     async with SessionLocal() as session:
#         job_applicants = await rq.get_applicants_by_job_id(session, job_id)
#         if job_applicants:
#             await query.answer("Applicants")
#             keyboard = await nav.create_job_applicants_keyboard(job_applicants, job_id)
#             # summary = await post_summary(my_job)
#             await query.message.edit_text(text="Applicants", parse_mode=ParseMode.HTML, reply_markup=keyboard) 
#         else:
#             await query.message.edit_text("There are no applicants yet")
#             await handle_job_list_by_query(query, callback_data, state)
            
# @job_router.callback_query(nav.ApplicantsCallback.filter(F.action == "manage"))
# async def handle_job_check_applicants_callback(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
#     # user_id = query.from_user.id
#     applicant_id = int(callback_data.id)
#     job_id = int(callback_data.job_id)
#     async with SessionLocal() as session:
#         # Later change to RESUME search
#         user = await rq.get_user(session, applicant_id)
#         if user:
#             await query.answer("Applicant")
#             keyboard = await nav.create_single_applicant_keyboard(applicant_id, job_id)
#             summary = markdown.text(
#                 markdown.hbold(f'{user.name}'),
#                 markdown.hunderline(f'{user.user_id} - '),
#                 markdown.hblockquote(f'{user.city}')
#             )
#             # summary = await post_summary(my_job)
#             await query.message.edit_text(text=summary, parse_mode=ParseMode.HTML, reply_markup=keyboard) 
#         else:
#             await query.message.answer("There are no applicants yet")
    


    
#     # job_id = int(callback_data.id)
#     # await query.answer("Applicants")
#     # keyboard = await nav.create_edit_job_keyboard(job_id)
#     # await query.message.edit_text("What do you want to edit?", reply_markup=keyboard)

# @job_router.callback_query(nav.JobsCallback.filter(F.action == "edit"))
# async def handle_job_edit_callback(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
#     job_id = int(callback_data.id)
#     await query.answer("Edit")
#     keyboard = await nav.create_edit_job_keyboard(job_id)
#     await query.message.edit_text("What do you want to edit?", reply_markup=keyboard)
# @job_router.callback_query(nav.JobsCallback.filter())
# async def handle_job_field_edit_callback(query: CallbackQuery, callback_data: nav.JobsCallback, state: FSMContext):
#     job_id = int(callback_data.id)
#     await state.set_state(JobEdit.job_id)
#     await state.update_data(job_id=job_id)
#     await state.set_state(JobEdit.chat_instance)
#     await state.update_data(chat_instance=query.chat_instance)
#     await query.answer(f"{callback_data.action.capitalize()}")
#     match callback_data.action:
#         case "title":
#             await state.set_state(JobEdit.title)
#             await query.message.answer("Provide new title")
#         case "description":
#             await state.set_state(JobEdit.description)
#             await query.message.edit_text("Provide new description")
#         case "skills":
#             await state.set_state(JobEdit.skills)
#             await query.message.answer("Provide new skills")
#         case "city":
#             await state.set_state(JobEdit.location)
#             await query.message.answer("Provide new city")
#         case "address":
#             await state.set_state(JobEdit.address)
#             await query.message.answer("Provide new address")

# @job_router.message(JobEdit.title, F.text)
# @job_router.message(JobEdit.description, F.text)
# @job_router.message(JobEdit.skills, F.text)
# @job_router.message(JobEdit.location, F.location)
# @job_router.message(JobEdit.location, F.text)
# @job_router.message(JobEdit.address, F.location)
# @job_router.message(JobEdit.address, F.text)
# async def handle_job_field_update_callback(message: Message, state: FSMContext):
#     current_state = await state.get_state()
#     data = await state.get_data()
#     job_id = data["job_id"]
#     chat_instance = data["chat_instance"]
#     callback_data = nav.JobsCallback(id=str(job_id), action="list")
#     # query = CallbackQuery(
#     # id="1",
#     # from_user=User(id=message.from_user.id, is_bot=False, first_name="Test"),
#     # message=Message(
#     #     message_id=1,
#     #     date="2021-01-01",
#     #     chat=Chat(id=123456, type="private", first_name="Test"),
#     #     text="Test message"
#     # ), chat_instance=chat_instance,
#     # data="callback_data")
#     match current_state:
#         case JobEdit.title.state:
#             print("JOB ID", job_id)
#             print("Current State", current_state)
#             # DB query to edit field
#             async with SessionLocal() as session:
#                 updated = await rq.update_job_by_id(session, job_id, JobModel.title, message.text) 
#                 if updated:
#                     await message.answer("Title successfully updated")
#                     await handle_job_list_by_message(message, callback_data, state)
#                 else: 
#                     await message.answer("Error")
#         case JobEdit.description.state:
#             async with SessionLocal() as session:
#                 updated = await rq.update_job_by_id(session, job_id, JobModel.description, message.text) 
#                 if updated:
#                     await message.answer("Description successfully updated")
#                     await handle_job_list_by_message(message, callback_data, state)
#                 else: 
#                     await message.answer("Error")
#         case JobEdit.skills.state:
#             async with SessionLocal() as session:
#                 updated = await rq.update_job_by_id(session, job_id, JobModel.skills, message.text) 
#                 if updated:
#                     await message.answer("Skills successfully updated")
#                     await handle_job_list_by_message(message, callback_data, state)
#                 else: 
#                     await message.answer("Error")
#         case JobEdit.location.state:
#             if message.location:
#                 user_location = location.get_location(message.location.latitude, message.location.longitude)
#                 print(user_location)
#                 address = user_location[1]
#                 async with SessionLocal() as session:
#                     updated = await rq.update_job_by_id(session, job_id, JobModel.city, address)
#                     if updated:
#                         await message.answer("City successfully updated")
#                         await handle_job_list_by_message(message, callback_data, state)
#                     else: 
#                         await message.answer("Error")
#             else:
#                 async with SessionLocal() as session:
#                     updated = await rq.update_job_by_id(session, job_id, JobModel.city, message.text) 
#                     if updated:
#                         await message.answer("City successfully updated")
#                         await handle_job_list_by_message(message, callback_data, state)
#                     else: 
#                         await message.answer("Error")
#         case JobEdit.address.state:
#             if message.location:
#                 user_location = location.get_location(message.location.latitude, message.location.longitude)
#                 print(user_location)
#                 address = user_location[0]
#                 async with SessionLocal() as session:
#                     updated = await rq.update_job_by_id(session, job_id, JobModel.address, address)
#                     if updated:
#                         await message.answer("Address successfully updated")
#                         await handle_job_list_by_message(message, callback_data, state)
#                     else: 
#                         await message.answer("Error")
#             else:
#                 async with SessionLocal() as session:
#                     updated = await rq.update_job_by_id(session, job_id, JobModel.address, message.text) 
#                     if updated:
#                         await message.answer("Address successfully updated")
#                         await handle_job_list_by_message(message, callback_data, state)
#                     else: 
#                         await message.answer("Error")
#     # await my_job_posts_by_query(query, state)



# # ---NEW POST---
# @job_router.message(Jobs.choice, F.text == "Post an ad 📰")
# async def job(message: Message, state: FSMContext):
#     await message.answer("Creating your ad...\
#                          \nMind that you can always \nGo /back or /cancel the process")
#     await state.set_state(Job.title)
#     await message.answer("Type the title for your ad:", reply_markup=ReplyKeyboardRemove())
#     await set_back_commands(id=message.from_user.id)
# @job_router.callback_query(nav.MenuCallback.filter(F.menu == "my_job_ads"))
# async def job_by_query(query: CallbackQuery, state: FSMContext):
#     await query.message.edit_text("Creating your ad...\
#                          \nMind that you can always \nGo /back or /cancel the process")
#     await state.set_state(Job.title)
#     await query.message.answer("Type the title for your ad:", reply_markup=ReplyKeyboardRemove())
#     await set_back_commands(id=query.from_user.id)



# # --- POST CREATION ---
# @job_router.message(Job.title, F.text)
# async def job_title(message: Message, state: FSMContext):
#     await state.update_data(title=message.text)
#     await state.set_state(Job.description)
#     await message.answer(f"Now, provide some description for {html.bold(message.text)}:")
# @job_router.message(Job.description, F.text)
# async def job_description(message: Message, state: FSMContext):
#     await state.update_data(description=message.text)
#     await state.set_state(Job.skills)
#     await message.answer("Ok, now provide skills that are required for your job:")
# @job_router.message(Job.skills, F.text)
# async def job_skills(message: Message, state: FSMContext):
#     await state.update_data(skills=message.text)
#     await state.set_state(Job.location)
#     await message.answer(f"Ok, now provide the location for your job:", reply_markup=nav.locationMenu)
# @job_router.message(Job.location, F.location)
# async def job_location(message: Message, state: FSMContext):
#     user_location = location.get_location(message.location.latitude, message.location.longitude)
#     print(user_location)
#     await state.update_data(location=user_location[1])
#     data = await state.update_data(address=user_location[0])
#     new_job = NewJob(True, message.from_user.id, data["title"], data["description"], data["skills"], data["location"], data["address"], message.location.latitude, message.location.longitude)
#     await state.clear()
#     await show_summary(message=message, data=data)
#     # make database request to add post
#     async with SessionLocal() as session:
#         job_post = await rq.add_job_post_to_user(session, new_job)
#         print("Job post added successfully", job_post)
#     await state.set_state(Jobs.choice)
#     await message.answer("Good, your ad is successfully posted!", reply_markup=nav.jobsReplyChoiceMenu)
#     await set_default_commands(id=message.from_user.id)
# @job_router.message(Job.location, F.text)
# async def job_city(message: Message, state: FSMContext):
#     city = message.text.strip().capitalize()
#     await state.update_data(location=city)
#     await state.set_state(Job.address)
#     await message.answer("Add an address (street) for your post")
# @job_router.message(Job.address, F.text)
# async def job_address(message: Message, state: FSMContext):
#     data = await state.update_data(address=message.text)
#     new_job = NewJob(False, message.from_user.id, data["title"], data["description"], data["skills"], data["location"], data["address"])
#     await state.clear()
#     await show_summary(message=message, data=data)
#     # make database request to add post
#     async with SessionLocal() as session:
#         job_post = await rq.add_job_post_to_user(session, new_job)
#         print("Job post added successfully", job_post)
#     await state.set_state(Jobs.choice)
#     await message.answer("Good, your ad is successfully posted!", reply_markup=nav.jobsReplyChoiceMenu)

# async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
#     title = data["title"]
#     description = data["description"]
#     skills = data["skills"]
#     location = data["location"]
#     # summary = text(
#     #     text(f"{html.underline('Job overview:\n')}"),
#     #     text(f"{html.bold('Title:')} {title}\n"),
#     #     text(f"{html.bold('Description:')} {html.italic(description)}\n"),
#     #     text(f"{html.bold('Skills (required):')} {html.code(skills)}"),
#     #     text(f"{html.blockquote(location)}"),
#     # )
#     summary = markdown.text(
#                 markdown.hbold(f'{title}\n'),
#                 markdown.hcode(f'{description}\n'),
#                 markdown.text('Skills required:'),
#                 markdown.hitalic(f'{skills}'),
#                 markdown.hblockquote(f'{location}')
#             )
#     await message.answer(text=summary, reply_markup=ReplyKeyboardRemove())



# # --- NEXT ---
# @job_router.message(Jobs.searching, F.text == "Next ➡️")
# async def next_job(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     # await state.set_state(Jobs.searching)
#     async with SessionLocal() as session:
#         user = await rq.get_user(session, user_id)
#         # job = await rq.get_next_job_by_id(session, user.jobs_search_id_list)
#         job = await search_funcitons_map[user.jobs_city_search](session, user.jobs_search_id_list, user.city, user_id)
#         if job:
#             summary = await post_summary(job)
#             await message.answer(text=summary, parse_mode=ParseMode.HTML, reply_markup=nav.applyMenu.as_markup()) 
#             await rq.add_id_to_user_jobs_search_id_list(session, user.user_id, job.id)
#         elif job is None:
#             if user.jobs_city_search:
#                 await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
#                 await message.answer("Would you like to search job options outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
#             else:
#                 await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
#                 await message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  
#         else:
#             await message.answer("No more job posts", reply_markup=ReplyKeyboardRemove())
#             await message.answer("You can come later to see new available job vacations", reply_markup=nav.jobsChoiceMenu.as_markup())  



# # --- JOB APPLICATION ---
# @job_router.callback_query(Jobs.searching, nav.ApplyCallback.filter(F.action == "apply"))
# async def apply_for_job(query: CallbackQuery, state: FSMContext):
#     user_id = query.from_user.id
#     async with SessionLocal() as session:
#          user = await rq.get_user(session, user_id)
#          job_application = await rq.apply_for_job(session, user.jobs_search_id, user.user_id)
#     await query.answer('Applied')
#     await query.message.edit_reply_markup(reply_markup=nav.appliedMenu.as_markup())
# @job_router.callback_query(Jobs.searching, nav.ApplyCallback.filter(F.action == "applied"))
# async def applied(query: CallbackQuery, state: FSMContext):
#     await query.answer("Already Applied")



# # --- HELPER FUNCTIONS ---
# async def post_summary(job: Job): # use ParseMode.HTML (parse_mode=ParseMode.HTML)
#     job_skills: str = job.skills
#     skills_list: list = job_skills.split(',')
#     skills_formatted = "\n".join([f"- {skill.strip().capitalize()}" for skill in skills_list])
#     summary = (
#         f"<b>{job.title}</b>\n\n"
#         f"<code>{job.description}</code>\n\n"
#         "Skills required:\n"
#         f"{skills_formatted}\n\n"
#         f"<i>📍 {(job.city).capitalize()}, {job.address}</i>"
#     )
#     return summary


# # --- ERROR HANDLING --- 
#     # choice = State()
#     # searching = State()

#     # title = State()
#     # description = State()
#     # skills = State()
#     # location = State()
#     # # optional
#     # address = State()
    
# @job_router.message(Jobs.choice)
# async def choice_invalid(message: Message):
#     await message.answer("I don't understand you. Please choose your action or Go /home")
# @job_router.message(Jobs.searching)
# async def searching_invalid(message: Message):
#     await message.answer("I don't understand you")
# @job_router.message(Job.title)
# async def title_invalid(message: Message):
#     await message.answer("I don't understand you")
# @job_router.message(Job.description)
# async def description_invalid(message: Message):
#     await message.answer("I don't understand you")
# @job_router.message(Job.skills)
# async def skills_invalid(message: Message):
#     await message.answer("I don't understand you")
# @job_router.message(Job.location)
# async def location_invalid(message: Message):
#     await message.answer("I don't understand you")
# @job_router.message(Job.address)
# async def address_invalid(message: Message):
#     await message.answer("I don't understand you")

# @job_router.callback_query(nav.ApplyCallback.filter(F.menu == "apply"))
# async def apply_invalid(query: CallbackQuery):
#     await query.message.answer("I don't understand")
# @job_router.callback_query(nav.ApplyCallback.filter(F.menu == "applied"))
# async def applied_invalid(query: CallbackQuery):
#     await query.message.answer("I don't understand")

# @job_router.callback_query(nav.MenuCallback.filter(F.menu == "post_job"))
# async def post_job_invalid(query: CallbackQuery):
#     await query.message.answer("I don't understand")
# @job_router.callback_query(nav.MenuCallback.filter(F.menu == "my_job_ads"))
# async def my_bio_ads_invalid(query: CallbackQuery):
#     await query.message.answer("I don't understand")
# @job_router.callback_query(nav.MenuCallback.filter(F.menu == "jobs_go_search_beyond"))
# async def go_search_beyond_invalid(query: CallbackQuery):
#     await query.message.answer("I don't understand")