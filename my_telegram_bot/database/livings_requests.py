from sqlalchemy.future import select
from sqlalchemy import BigInteger, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Living, LivingPhoto
import random


# --- USER ---
async def get_user(db: AsyncSession, user_id: BigInteger):
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()
    return user
async def get_user_username_by_id(db: AsyncSession, user_id: BigInteger):
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()
    return user.username
async def add_username_to_user_by_id(db: AsyncSession, user_id: BigInteger, new_username: str):
    result = await db.execute(update(User).where(User.user_id == user_id).values(username=new_username))
    await db.commit()
    return result 


# --- HANDLE PHOTOS ---
async def add_photos_to_living(db: AsyncSession, living_id: int, photos: list):
    print("IM IN ADDING PHOTOS")
    for photo in photos:
        new_photo = LivingPhoto(living_id=living_id, photo_id=photo)
        db.add(new_photo)
    await db.commit()
async def remove_existing_photos(db: AsyncSession, existing_living: Living):
    print("IM IN REMOVING PHOTOS")
    await db.refresh(existing_living)
    for photo in existing_living.photos:
        await db.delete(photo)
    await db.commit()


# --- HANDLE SALE ITEM ---
async def add_living_to_user_by_id(db: AsyncSession, living, photos):
    db_living = Living(
            user_id=living.user_id,
            username = living.username,
            description = living.description,
            price = living.price,
            city = living.city,
            address = living.address
        )
    db.add(db_living)
    await db.commit()
    await db.refresh(db_living)
    await add_photos_to_living(db, db_living.id, photos)
    return db_living


# --- USER FEATURES ---    
async def add_id_to_user_livings_search_id_list(db: AsyncSession, user_id, living_id):
    stmt = select(User).filter(User.user_id == user_id)
    result = await db.execute(stmt)
    user: User = result.scalars().first()
    search_ids = user.get_livings_search_id_list()
    search_ids.append(living_id)
    stmt = update(User).filter(User.user_id == user_id).values(livings_search_id_list = search_ids).values(livings_search_id = living_id)
    res = await db.execute(stmt)
    await db.commit()
    return res
async def update_my_livings_city_search(db: AsyncSession, my_id, new_livings_city_search: bool):
    print('id to be updated', new_livings_city_search)
    stmt = update(User).filter(User.user_id == my_id).values(items_city_search=new_livings_city_search)
    res = await db.execute(stmt)
    await db.commit()
    return res


# --- HANDLE SEARCH ---
async def get_next_living_with_city(db: AsyncSession, exclude_living_ids: list, city: str):
    if exclude_living_ids is None:
        exclude_living_ids = []
    stmt = ( # Query items excluding those in the exclude_item_ids list and filtering by city
        select(Living).filter(Living.id.notin_(exclude_living_ids), Living.city == city).order_by(Living.id)
    )
    result = await db.execute(stmt)
    livings = result.scalars().all()  # Ensure unique items are returned
    if livings:
        living = random.choice(livings) # Randomly choose one item from the list
        await db.refresh(living, attribute_names=["photos"])
        return living, living.photos
    return None, None
async def get_next_living_without_city(db: AsyncSession, exclude_living_ids: list, city: str):
    if exclude_living_ids is None:
        exclude_living_ids = []
    stmt = ( # Query items excluding those in the exclude_item_ids list and filtering by city
        select(Living)
        .filter(Living.id.notin_(exclude_living_ids), Living.city != city)
        .order_by(Living.id)
    )
    result = await db.execute(stmt)
    livings = result.scalars().all()  # Ensure unique items are returned
    if livings:
        living = random.choice(livings) # Randomly choose one item from the list
        await db.refresh(living, attribute_names=["photos"])
        return living, living.photos
    return None, None
# END