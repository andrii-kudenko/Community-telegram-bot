from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# --- MENUS ---
class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

class SalesCallback(CallbackData, prefix="sales"):
    id: str
    action: str
    additional: str

class BlankCallback(CallbackData, prefix="empty"):
    text: str

# --- SEARCH ---
# btnSearch = KeyboardButton(text='Search 🔎')
# btnPost = KeyboardButton(text='Post an ad 📦')
# btnMyPosts = KeyboardButton(text='View my sale ads🧾')
# salesReplyChoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSearch], [btnPost], [btnMyPosts]])
salesReplyChoiceMenu = InlineKeyboardBuilder()
salesReplyChoiceMenu.button(text="Search 🔎", callback_data=SalesCallback(id="0", action="search", additional="").pack())
salesReplyChoiceMenu.button(text="Post an ad 📦", callback_data=SalesCallback(id="0", action="post_item", additional="").pack())
salesReplyChoiceMenu.button(text="View my sale ads🧾", callback_data=MenuCallback(menu="my_items").pack())
salesReplyChoiceMenu.button(text="Go home 🏠", callback_data=MenuCallback(menu="home").pack())
salesReplyChoiceMenu.adjust(2, 1)

btnNext = KeyboardButton(text='Next ➡️')
nextMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnNext]])


# --- HANDLE PHOTOS ---
btnSavePhoto1 = KeyboardButton(text='Continue with 1/3 photos')
photosUploadingReplyMenu1 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto1]])
btnSavePhoto2 = KeyboardButton(text='Continue with 2/3 photos')
photosUploadingReplyMenu2 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnSavePhoto2]])


# --- LOCATION ---
btnLocation = KeyboardButton(text='Provide Location', request_location=True)
locationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnLocation]])




salesChoiceMenu = InlineKeyboardBuilder() # When there are no more profiles to look
salesChoiceMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
salesChoiceMenu.button(text='Post item 📰', callback_data=SalesCallback(id="0", action="post_item", additional="").pack())
salesChoiceMenu.button(text='My items', callback_data=MenuCallback(menu="my_items").pack())
salesChoiceMenu.adjust(2)

askToSearchBeyondMenu = InlineKeyboardBuilder() 
askToSearchBeyondMenu.button(text='Go home 🏠', callback_data=MenuCallback(menu="home").pack())
askToSearchBeyondMenu.button(text='Search beyond city 🔎', callback_data=SalesCallback(id="0", action="search_beyond", additional="").pack())

async def create_blank_keyboard(text):
    blankMenu = InlineKeyboardBuilder()
    blankMenu.button(text=f"{text}", callback_data=BlankCallback(text=f"{text}").pack())
    return blankMenu.as_markup()

# create_items_keyboard
# create_single_item_keyboard
# create_edit_item_keyboard

async def create_items_keyboard(items):
    itemsAllMenu = InlineKeyboardBuilder()
    for item in items:
        itemsAllMenu.button(text=item.title, callback_data=SalesCallback(id=str(item.id), action="manage", additional=f"{item.title}").pack())
    itemsAllMenu.button(text="Back", callback_data=SalesCallback(id=str(item.id), action="start_sales", additional="Back").pack())
    itemsAllMenu.adjust(2)
    return itemsAllMenu.as_markup()

async def create_single_item_keyboard(id, title, photos):
    photo_ids = [str(photo.id) for photo in photos]
    photos_string = ",".join(photo_ids)
    itemMenu = InlineKeyboardBuilder()
    itemMenu.button(text="✏️ Edit", callback_data=SalesCallback(id=str(id), action="edit", additional=str(photos_string)).pack())
    itemMenu.button(text="🗑️ Delete", callback_data=SalesCallback(id=str(id), action="delete", additional=title).pack()) # ❌
    itemMenu.button(text="Back", callback_data=SalesCallback(id="0", action="my_items", additional="Back").pack())
    itemMenu.adjust(2)
    return itemMenu.as_markup()

async def create_edit_item_keyboard(id, photos_string):
    photo_ids = photos_string.split(",")
    editMenu = InlineKeyboardBuilder()
    editMenu.button(text="Title", callback_data=SalesCallback(id=str(id), action="title", additional="0").pack())
    editMenu.button(text="Description", callback_data=SalesCallback(id=str(id), action="description", additional="0").pack())
    editMenu.button(text="Price", callback_data=SalesCallback(id=str(id), action="price", additional="0").pack())
    editMenu.button(text="City", callback_data=SalesCallback(id=str(id), action="city", additional="0").pack())
    editMenu.button(text="Location", callback_data=SalesCallback(id=str(id), action="address", additional="0").pack())
    for i in range(len(photo_ids)):
        editMenu.button(text=f"Photo {i+1}", callback_data=SalesCallback(id=str(id), action=f"photo{i+1}", additional=f"{photo_ids[i]}").pack())
    editMenu.button(text="Back", callback_data=SalesCallback(id=str(id), action="manage", additional="Back").pack())
    editMenu.adjust(2)
    return editMenu.as_markup()

