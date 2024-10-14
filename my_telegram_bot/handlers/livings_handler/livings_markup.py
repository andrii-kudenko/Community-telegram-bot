from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# --- MENUS ---
class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

class LivingsCallback(CallbackData, prefix="livings"):
    id: str
    action: str
    additional: str

class BlankCallback(CallbackData, prefix="empty"):
    text: str



# # --- SEARCH ---
# btnSearch = KeyboardButton(text='Search 🔎')
# btnPost = KeyboardButton(text='Post an ad 📰')
# btnMyPosts = KeyboardButton(text='View my living ads 🧾')
# livingsReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost], [btnMyPosts]])

livingsReplyChoiceMenu = InlineKeyboardBuilder()
livingsReplyChoiceMenu.button(text="Search 🔎", callback_data=LivingsCallback(id="0", action="search", additional="").pack())
livingsReplyChoiceMenu.button(text="Post an ad 📰", callback_data=LivingsCallback(id="0", action="post_ad", additional="").pack())
livingsReplyChoiceMenu.button(text="View my living ads 🧾", callback_data=MenuCallback(menu="my_livings").pack())
livingsReplyChoiceMenu.button(text="Go home 🏠", callback_data=MenuCallback(menu="home").pack())
livingsReplyChoiceMenu.adjust(2, 1)

btnNext = KeyboardButton(text='Next ➡️')
nextMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnNext]])


# --- HANDLE PHOTOS ---
btnSavePhoto1 = KeyboardButton(text='Continue with 1/6 photos')
photosUploadingReplyMenu1 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto1]])
btnSavePhoto2 = KeyboardButton(text='Continue with 2/6 photos')
photosUploadingReplyMenu2 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto2]])
btnSavePhoto3 = KeyboardButton(text='Continue with 3/6 photos')
photosUploadingReplyMenu3 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto3]])
btnSavePhoto4 = KeyboardButton(text='Continue with 4/6 photos')
photosUploadingReplyMenu4 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto4]])
btnSavePhoto5 = KeyboardButton(text='Continue with 5/6 photos')
photosUploadingReplyMenu5 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto5]])


# --- LOCATION ---
btnLocation = KeyboardButton(text='Provide Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])




livingsChoiceMenu = InlineKeyboardBuilder() # When there are no more profiles to look
livingsChoiceMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
livingsChoiceMenu.button(text='Post living 📰', callback_data=LivingsCallback(id="0", action="post_ad", additional="Back").pack())
livingsChoiceMenu.button(text='My livings', callback_data=MenuCallback(menu="my_livings").pack())
livingsChoiceMenu.adjust(2,1)

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=LivingsCallback(id="0", action="search_beyond", additional="Back").pack())

async def create_blank_keyboard(text):
    blankMenu = InlineKeyboardBuilder()
    blankMenu.button(text=f"{text}", callback_data=BlankCallback(text=f"{text}").pack())
    return blankMenu.as_markup()


async def create_livings_keyboard(items):
    livingsAllMenu = InlineKeyboardBuilder()
    for item in items:
        livingsAllMenu.button(text=f"{item.description[:15]}...", callback_data=LivingsCallback(id=str(item.id), action="manage", additional=f"{item.description[:15]}...").pack())
    livingsAllMenu.button(text="Back", callback_data=LivingsCallback(id=str(item.id), action="start_livings", additional="Back").pack())
    livingsAllMenu.adjust(2)
    return livingsAllMenu.as_markup()

async def create_single_living_keyboard(id, title, photos):
    photo_ids = [str(photo.id) for photo in photos]
    photos_string = ",".join(photo_ids)
    livingMenu = InlineKeyboardBuilder()
    livingMenu.button(text="✏️ Edit", callback_data=LivingsCallback(id=str(id), action="edit", additional=str(photos_string)).pack())
    livingMenu.button(text="🗑️ Delete", callback_data=LivingsCallback(id=str(id), action="delete", additional=title).pack()) # ❌
    livingMenu.button(text="Back", callback_data=LivingsCallback(id="0", action="my_livings", additional="Back").pack())
    livingMenu.adjust(2)
    return livingMenu.as_markup()

async def create_edit_living_keyboard(id, photos_string):
    photo_ids = photos_string.split(",")
    editMenu = InlineKeyboardBuilder()
    editMenu.button(text="Title", callback_data=LivingsCallback(id=str(id), action="title", additional="0").pack())
    editMenu.button(text="Description", callback_data=LivingsCallback(id=str(id), action="description", additional="0").pack())
    editMenu.button(text="Price", callback_data=LivingsCallback(id=str(id), action="price", additional="0").pack())
    editMenu.button(text="City", callback_data=LivingsCallback(id=str(id), action="city", additional="0").pack())
    editMenu.button(text="Address", callback_data=LivingsCallback(id=str(id), action="address", additional="0").pack())
    for i in range(len(photo_ids)):
        editMenu.button(text=f"Photo {i+1}", callback_data=LivingsCallback(id=str(id), action=f"photo_{i+1}", additional=f"{photo_ids[i]}").pack())
    editMenu.button(text="Back", callback_data=LivingsCallback(id=str(id), action="manage", additional="Back").pack())
    editMenu.adjust(2)
    return editMenu.as_markup()