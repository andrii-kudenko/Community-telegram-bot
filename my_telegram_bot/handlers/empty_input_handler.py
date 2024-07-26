from aiogram import Router
from aiogram.types import Message 

empty_router = Router(name=__name__)

# @empty_router.message()
# async def catch_empty(message: Message):
#     await message.answer("Please, provide a valid answer empty")