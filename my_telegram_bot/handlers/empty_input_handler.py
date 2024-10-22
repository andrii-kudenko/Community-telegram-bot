from aiogram import Router
from aiogram.types import Message 
empty_router = Router(name=__name__)
# @empty_router.message()
# async def catch_empty(message: Message):
#     await message.answer("Please, provide a valid answer empty")



# ###

# @living_router.message(Command("livings", prefix=("!/")))
# async def start_livings(message: Message, state: FSMContext):
#     await message.answer("Hi there! Choose the action:", reply_markup=nav.livingsReplyChoiceMenu.as_markup())
# @living_router.callback_query(nav.MenuCallback.filter(F.menu == "start_livings"))
# async def start_livings_by_query(query: CallbackQuery, callback_data: nav.MenuCallback, state: FSMContext): # HAS Middleware
#     # ...
#     await query.message.answer("Hi there! Choose the action:", reply_markup=nav.livingsReplyChoiceMenu.as_markup())


# @living_router.message(Living.description, Command("cancel", prefix=("!/")))
# @living_router.message(Living.photo1, Command("cancel", prefix=("!/")))
# @living_router.message(Living.photo2, Command("cancel", prefix=("!/")))
# @living_router.message(Living.photo3, Command("cancel", prefix=("!/")))
# @living_router.message(Living.photo4, Command("cancel", prefix=("!/")))
# @living_router.message(Living.photo5, Command("cancel", prefix=("!/")))
# @living_router.message(Living.photo6, Command("cancel", prefix=("!/")))
# @living_router.message(Living.price, Command("cancel", prefix=("!/")))
# @living_router.message(Living.location, Command("cancel", prefix=("!/")))
# @living_router.message(Living.address, Command("cancel", prefix=("!/")))
# async def cancel_handler(message: Message, state: FSMContext) -> None:
#     current_state = await state.get_state()
#     if current_state is None:
#         return

#     logging.info("Cancelling state %r", current_state)
#     await state.set_state(Livings.choice)
#     await message.answer(
#         "Cancelled",
#         reply_markup=nav.livingsChoiceMenu.as_markup(),
#     )
#     await set_default_commands(id=message.from_user.id)

# @living_router.message(Living.description, Command("back", prefix=("!/")))
# @living_router.message(Living.price, Command("back", prefix=("!/")))
# @living_router.message(Living.location, Command("back", prefix=("!/")))
# async def back_handler(message: Message, state: FSMContext) -> None:
#     current_state = await state.get_state()
#     if current_state == Living.description:
#         await state.set_state(Livings.choice)
#         await message.answer("Choose action:", reply_markup=nav.livingsReplyChoiceMenu.as_markup())
#     elif current_state == Living.photo1:
#         await state.set_state(Living.description)
#         await message.answer("Send me new description")
#     elif current_state == Living.photo2:
#         await state.set_state(Living.photo1)
#         await message.answer("Send me another photo")
#     elif current_state == Living.photo3:
#         await state.set_state(Living.photo2)
#         await message.answer("Send me another photo")
#     elif current_state == Living.photo4:
#         await state.set_state(Living.photo3)
#         await message.answer("Send me another photo")
#     elif current_state == Living.photo5:
#         await state.set_state(Living.photo4)
#         await message.answer("Send me another photo")
#     elif current_state == Living.photo6:
#         await state.set_state(Living.photo5)
#         await message.answer("Send me another photo")
#     elif current_state == Living.price:
#         await state.set_state(Living.photo6)
#         await message.answer("Send me another photo")
#     elif current_state == Living.location:
#         await state.set_state(Living.price)
#         await message.answer("Send me new price")
#     elif current_state == Living.address:
#         await state.set_state(Living.location)
#         await message.answer("Send me new location")
#     else:
#         pass



# # --- SEARCH ---
# @living_router.callback_query(nav.LivingsCallback.filter(F.action == "search"))
# async def search_by_query(query: CallbackQuery, state: FSMContext):
#     user_id = query.from_user.id
#     await query.answer("Searching")
#     updated_keyboard = await nav.create_blank_keyboard("Search 🔎")
#     await query.message.edit_reply_markup(reply_markup=updated_keyboard)  
#     # database call
#     async with SessionLocal() as session:
#         await rq.update_my_livings_city_search(session, user_id, True)
#     # await query.message.answer("Searching...", reply_markup=nav.nextMenu)
#     await state.set_state(Livings.searching)
#     async with SessionLocal() as session:
#         user = await rq.get_user(session, user_id)
#         living, photos = await rq.get_next_living_with_city(session, user.livings_search_id_list, user.city)
#         if living:
#             await query.message.answer("Searching...", reply_markup=nav.nextMenu)
#             summary = await living_summary(living, photos)
#             await query.message.answer_media_group(media=summary)
#             await rq.add_id_to_user_livings_search_id_list(session, user.user_id, living.id)
#             # updated = await rq.add_id_to_user_sales_jobs_search_id_list()
#         elif living is None:
#             await query.message.answer("Searching...")
#             await query.message.answer("No more livings options", reply_markup=ReplyKeyboardRemove())
#             await query.message.answer("Would you like to search for livings outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())
#         else:
#             await query.message.answer("Searching...")
#             await query.message.answer("No more livings posts", reply_markup=ReplyKeyboardRemove())
#             await query.message.answer("You can come later to see new available livings options", reply_markup=nav.livingsChoiceMenu.as_markup())
# @living_router.callback_query(nav.MenuCallback.filter(F.menu == "livings_go_search_beyond"))
# async def search_beyond_by_query(query: CallbackQuery, state: FSMContext):
#     user_id = query.from_user.id
#     await query.answer("Searching beyond")
#     updated_keyboard = await nav.create_blank_keyboard("Search beyond city 🔎")
#     await query.message.edit_reply_markup(reply_markup=updated_keyboard)
#     async with SessionLocal() as session:
#         await rq.update_my_livings_city_search(session, user_id, False)
#     await query.message.answer("Searching...", reply_markup=nav.nextMenu)
#     await state.set_state(Livings.searching)
#     async with SessionLocal() as session:
#         user = await rq.get_user(session, user_id)
#         living, photos = await rq.get_next_living_without_city(session, user.livings_search_id_list, user.city)
#         if living:
#             await query.message.answer("Searching...", reply_markup=nav.nextMenu)
#             summary = await living_summary(living, photos)
#             await query.message.answer_media_group(media=summary)
#             await rq.add_id_to_user_livings_search_id_list(session, user.user_id, living.id)
#         elif living is None:
#             await query.message.answer("Searching...")
#             await query.message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
#             await query.message.answer("You can come later to see new available sales options", reply_markup=nav.livingsChoiceMenu.as_markup()) 
#         elif living is None:
#             await query.message.answer("Searching...")
#             await query.message.answer("No more sales posts", reply_markup=ReplyKeyboardRemove())
#             await query.message.answer("You can come later to see new available sales options", reply_markup=nav.livingsChoiceMenu.as_markup()) 



# # --- MY POSTS ---
# @living_router.callback_query(nav.MenuCallback.filter(F.menu == "my_livings"))
# async def my_livings_by_query(query: CallbackQuery, state: FSMContext):
#     user_id = query.from_user.id
#     await query.answer("My Ads")
#     updated_keyboard = await nav.create_blank_keyboard("View my living ads 🧾")
#     await query.message.edit_reply_markup(reply_markup=updated_keyboard)
#     # make a database request
#     # and further manipulations
#     async with SessionLocal() as session:        
#         print("new_job")
#     await query.message.answer("My posts")


# # --- NEW LIVING ---
# @living_router.callback_query(nav.LivingsCallback.filter(F.action == "post_ad"))
# async def new_living_by_query(query: CallbackQuery, state: FSMContext):
#     await query.answer("Creating New Post")
#     updated_keyboard = await nav.create_blank_keyboard("Post item 📰")
#     await query.message.edit_reply_markup(reply_markup=updated_keyboard)
#     await query.message.answer("Creating your ad...\
#                          \nMind that you can always \nGo /back or /cancel the process")
#     await state.set_state(Living.description)
#     await query.message.answer("Provide a full description for your ad:")
#     await set_back_commands(id=query.from_user.id)


# # --- LIVING CREATION ---
# @living_router.message(Living.description, F.text)
# async def living_description(message: Message, state: FSMContext):
#     await state.update_data(description=message.text)
#     await state.set_state(Living.photo1)
#     await message.answer(f"Ok, now you can upload up to 6 photos for your ad:")
# @living_router.message(Living.photo1, F.photo)
# async def ad_photo1(message: Message, state: FSMContext):
#     file_id = message.photo[-1].file_id
#     await state.update_data(photo1 = file_id)
#     await state.set_state(Living.photo2)
#     await message.answer("Nice, you have uploaded one photo. Send another one or just continue with this one", reply_markup=nav.photosUploadingReplyMenu1)
# @living_router.message(Living.photo2, F.photo)
# async def ad_photo2(message: Message, state: FSMContext):
#     file_id = message.photo[-1].file_id
#     await state.update_data(photo3 = file_id)
#     await state.set_state(Living.photo3)
#     await message.answer("Good, now you have 2 photos. Add more?", reply_markup=nav.photosUploadingReplyMenu2)
# @living_router.message(Living.photo3, F.photo)
# async def ad_photo2(message: Message, state: FSMContext):
#     file_id = message.photo[-1].file_id
#     await state.update_data(photo4 = file_id)
#     await state.set_state(Living.photo4)
#     await message.answer("Good, now you have 3 photos. Add more?", reply_markup=nav.photosUploadingReplyMenu3)
# @living_router.message(Living.photo4, F.photo)
# async def ad_photo2(message: Message, state: FSMContext):
#     file_id = message.photo[-1].file_id
#     await state.update_data(photo5 = file_id)
#     await state.set_state(Living.photo5)
#     await message.answer("Good, now you have 4 photos. Add more?", reply_markup=nav.photosUploadingReplyMenu4)
# @living_router.message(Living.photo5, F.photo)
# async def ad_photo2(message: Message, state: FSMContext):
#     file_id = message.photo[-1].file_id
#     await state.update_data(photo6 = file_id)
#     await state.set_state(Living.photo5)
#     await message.answer("Good, now you have 5 photos. Add more?", reply_markup=nav.photosUploadingReplyMenu5)
# @living_router.message(Living.photo6, F.photo)
# async def ad_photo3(message: Message, state: FSMContext):
#     file_id = message.photo[-1].file_id
#     await state.update_data(photo6 = file_id)
#     # await state.set_state(Living.photo6)
#     await message.answer("Cool, now you have 6 photos for you ad", reply_markup=ReplyKeyboardRemove())
#     await confirm_photos(message, state)
# @living_router.message(Living.photo2, F.text == "Continue with 1/6 photos")
# @living_router.message(Living.photo3, F.text == "Continue with 2/6 photos")
# @living_router.message(Living.photo4, F.text == "Continue with 3/6 photos")
# @living_router.message(Living.photo5, F.text == "Continue with 4/6 photos")
# @living_router.message(Living.photo6, F.text == "Continue with 5/6 photos")
# async def confirm_photos(message: Message, state: FSMContext):
#     await state.set_state(Living.price)
#     await message.answer(f"Ok, now provide price for your ad:", reply_markup=ReplyKeyboardRemove())
# @living_router.message(Living.price, F.text)
# async def living_price(message: Message, state: FSMContext):
#     await state.update_data(price=message.text)
#     await state.set_state(Living.location)
#     await message.answer(f"Ok, now provide the city for your place:", reply_markup=nav.locationMenu)
# @living_router.message(Living.location, F.location)
# async def living_location(message: Message, state: FSMContext):
#     user_location = location.get_location(message.location.latitude, message.location.longitude)
#     print(user_location)
#     await state.update_data(location=user_location[1])
#     data = await state.update_data(address=user_location[0])
#     new_living = NewLiving(message.from_user.id, message.from_user.username, data["description"], data["price"], data["location"], data["address"])
#     await state.clear()
#     await show_summary(message=message, data=data)
#     # make database request to add post
#     async with SessionLocal() as session:
#         photos = []
#         photos.append(data["photo1"])  
#         photos.append(data.get("photo2")) if data.get("photo2") else None
#         photos.append(data.get("photo3")) if data.get("photo3") else None
#         photos.append(data.get("photo4")) if data.get("photo4") else None
#         photos.append(data.get("photo5")) if data.get("photo5") else None
#         photos.append(data.get("photo6")) if data.get("photo6") else None
#         new_living_post = await rq.add_living_to_user_by_id(session, new_living, photos)
#         print("Living post added successfully", new_living_post)

#     await state.set_state(Livings.choice)
#     await message.answer("Good, your ad is successfully posted!", reply_markup=nav.livingsReplyChoiceMenu)
#     await set_default_commands(id=message.from_user.id)
# @living_router.message(Living.location, F.text)
# async def living_city(message: Message, state: FSMContext):
#     city = message.text.strip().capitalize()
#     await state.update_data(location=city)
#     await state.set_state(Living.address)
#     await message.answer("Add an address (street) for your post")
# @living_router.message(Living.address, F.text)
# async def living_address(message: Message, state: FSMContext):
#     data = await state.update_data(address=message.text)
#     new_living = NewLiving(message.from_user.id, message.from_user.username, data["description"], data["price"], data["location"], data["address"])
#     await state.clear()
#     await show_summary(message=message, data=data)
#     # make database request to add post
#     async with SessionLocal() as session:
#         photos = []
#         photos.append(data["photo1"])  
#         photos.append(data.get("photo2")) if data.get("photo2") else None
#         photos.append(data.get("photo3")) if data.get("photo3") else None
#         photos.append(data.get("photo4")) if data.get("photo4") else None
#         photos.append(data.get("photo5")) if data.get("photo5") else None
#         photos.append(data.get("photo6")) if data.get("photo6") else None
#         new_living_post = await rq.add_living_to_user_by_id(session, new_living, photos)
#         print("Living post added successfully", new_living_post)

#     await state.set_state(Livings.choice)
#     await message.answer("Good, your ad is successfully posted!", reply_markup=nav.livingsReplyChoiceMenu)

# async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True):
#     description = data["description"]
#     price = data["price"]
#     location = data["location"]
#     address = data["address"]
#     photos = []
#     photos.append(data["photo1"])  
#     photos.append(data.get("photo2")) if data.get("photo2") else None
#     photos.append(data.get("photo3")) if data.get("photo3") else None
#     photos.append(data.get("photo4")) if data.get("photo4") else None
#     photos.append(data.get("photo5")) if data.get("photo5") else None
#     photos.append(data.get("photo6")) if data.get("photo6") else None
#     # summary = text(
#     #     text(f"{html.underline('Job overview:\n')}"),
#     #     text(f"{html.bold('Title:')} {title}\n"),
#     #     text(f"{html.bold('Description:')} {html.italic(description)}\n"),
#     #     text(f"{html.bold('Skills (required):')} {html.code(skills)}"),
#     #     text(f"{html.blockquote(location)}"),
#     # )
#     summary = markdown.text(
#                 markdown.text(f'{description}\n'),
#                 markdown.hbold('Expected price: '),
#                 markdown.hitalic(f'{price}'),
#                 markdown.hblockquote(f'📍 {location}, {address}')
#             )
#     media = []
#     for photo in photos:
#         media.append(InputMediaPhoto(media=photo))
#     media[-1].caption = summary
#     await message.answer("New Living Post", reply_markup=ReplyKeyboardRemove())
#     await message.answer_media_group(media=media)



# # --- NEXT ---
# @living_router.message(Livings.searching, F.text == "Next ➡️")
# async def next_living(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     # await state.set_state(Jobs.searching)
#     async with SessionLocal() as session:
#         user = await rq.get_user(session, user_id)
#         # job = await rq.get_next_job_by_id(session, user.jobs_search_id_list)
#         living, photos = await search_funcitons_map[user.livings_city_search](session, user.livings_search_id_list, user.city)
#         if living:
#             summary = await living_summary(living, photos)
#             await message.answer_media_group(media=summary)
#             await rq.add_id_to_user_livings_search_id_list(session, user.user_id, living.id)
#         elif living is None:
#             if user.livings_city_search:
#                 await message.answer("No more livings options", reply_markup=ReplyKeyboardRemove())
#                 await message.answer("Would you like to search for livings outside of your city?", reply_markup=nav.askToSearchBeyondMenu.as_markup())  
#             else:
#                 await message.answer("No more livings posts", reply_markup=ReplyKeyboardRemove())
#                 await message.answer("You can come later to see new available livings options", reply_markup=nav.livingsChoiceMenu.as_markup())  
#         else:
#             await message.answer("No more livings posts", reply_markup=ReplyKeyboardRemove())
#             await message.answer("You can come later to see new available livings options", reply_markup=nav.livingsChoiceMenu.as_markup()) 





# # --- HELPER FUNCTIONS ---
# async def living_summary(living: Living, photos): # use ParseMode.HTML (parse_mode=ParseMode.HTML)
#     summary = markdown.text(
#                 markdown.text(f'{living.description}\n'),
#                 markdown.hbold('Expected price: '),
#                 markdown.hitalic(f'{living.price}'),
#                 markdown.hbold(f'\nLandlord ->'),
#                 markdown.hlink(f'@{living.username}', f'https://t.me/{living.username}'),
#                 markdown.hblockquote(f'📍 {living.city}, {living.address}')
#             )
#     media = []
#     for photo in photos:
#         media.append(InputMediaPhoto(media=photo.photo_id))
#     media[-1].caption = summary
#     return media