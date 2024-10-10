from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class ChoiceCallback(CallbackData, prefix="choice"):
    func: str

class MenuCallback(CallbackData, prefix="navigation"):
    menu: str

class BlankCallback(CallbackData, prefix="empty"):
    text: str

# categoryChoiceMenu = InlineKeyboardBuilder()
# categoryChoiceMenu.button(text='Jobs 💻', callback_data=ChoiceCallback(func="jobs").pack())
# categoryChoiceMenu.button(text='Livings 🛏', callback_data=ChoiceCallback(func="livings").pack())
# categoryChoiceMenu.button(text='Sales 💵', callback_data=ChoiceCallback(func="sales").pack())
# categoryChoiceMenu.button(text='Friends 🤼', callback_data=ChoiceCallback(func="friends").pack())
# categoryChoiceMenu.button(text='Profile 👤', callback_data=ChoiceCallback(func="profile").pack())
# categoryChoiceMenu.adjust(2, 2, 1)

categoryChoiceMenu = InlineKeyboardBuilder()
categoryChoiceMenu.button(text='Jobs 💻', callback_data=MenuCallback(menu="start_jobs").pack())
categoryChoiceMenu.button(text='Livings 🛏', callback_data=MenuCallback(menu="start_livings").pack())
categoryChoiceMenu.button(text='Sales 💵', callback_data=MenuCallback(menu="start_sales").pack())
categoryChoiceMenu.button(text='Friends 🤼', callback_data=MenuCallback(menu="start_friends").pack())
categoryChoiceMenu.button(text='Profile 👤', callback_data=MenuCallback(menu="start_profile").pack())
categoryChoiceMenu.adjust(2, 2, 1)



# btnMain = KeyboardButton(text='Main Menu')
# btnMain = 'Main Menu'

# --- Main Menu ---
# btnRandom = KeyboardButton(text='Random number')
# btnRandom = 'Random number'
# btnCompliment = KeyboardButton(text='Get Compliment')
# btnLocation = KeyboardButton(text='Get Location', request_location=True)
# btnCompliment = 'Get Compliment'
# btnExtra = KeyboardButton(text='More Functions')
# btnExtra = 'More Functions'
# mainMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[btnRandom, btnCompliment, btnExtra])
# mainMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnRandom], [btnCompliment], [btnLocation]])
# mainMenu.add(btnRandom, btnCompliment)

# --- Extra Menu ---
# btnInfo = KeyboardButton('Get info')
# btnText = KeyboardButton('Get text')
# extraMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[btnInfo, btnText, btnMain])

# btnBack = KeyboardButton(text='<- Go back')
# btnHome = KeyboardButton(text='Go home')
# navigationMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btnBack], [btnHome]])

# btnJob = InlineKeyboardButton(text='Jobs', callback_data="jobs")
# btnLiving = InlineKeyboardButton(text='Livings', callback_data="livings")
# btnSale = InlineKeyboardButton(text='Sales', callback_data="sales")
# btnFriend = InlineKeyboardButton(text='Friends', callback_data="friends")
# categoryChoiceMenu = InlineKeyboardMarkup(inline_keyboard=[[btnJob], [btnLiving], [btnSale], [btnFriend]])


btnPost = InlineKeyboardButton(text='Post', callback_data="post")
btnSearch = InlineKeyboardButton(text='Search ->', callback_data="search")
methodChoiceMenu = InlineKeyboardMarkup(inline_keyboard=[[btnPost], [btnSearch]])

async def create_blank_keyboard(text):
    blankMenu = InlineKeyboardBuilder()
    blankMenu.button(text=f"{text}", callback_data=BlankCallback(text=f"{text}").pack())
    return blankMenu.as_markup()