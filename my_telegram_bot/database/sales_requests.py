from sqlalchemy.future import select
from sqlalchemy import BigInteger, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Bio, BioPhoto, Like, SaleItem, SaleItemPhoto
import logging
import random


# ---USER---
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
async def add_photos_to_item(db: AsyncSession, item_id: int, photos: list):
    print("IM IN ADDING PHOTOS")
    for photo in photos:
        new_photo = SaleItemPhoto(sale_item_id=item_id, photo_id=photo)
        db.add(new_photo)
    await db.commit()
async def remove_existing_photos(db: AsyncSession, existing_item: SaleItem):
    print("IM IN REMOVING PHOTOS")
    await db.refresh(existing_item)
    for photo in existing_item.photos:
        await db.delete(photo)
    await db.commit()


# --- HANDLE SALE ITEM ---
async def add_item_to_user_by_id(db: AsyncSession, item, photos):
    db_item = SaleItem(
            user_id=item.user_id,
            username = item.username,
            title = item.title,
            description = item.description,
            price = item.price,
            city = item.city
        )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    await add_photos_to_item(db, db_item.id, photos)
    # for photo in photos:
    #     new_photo = BioPhoto(bio_id=db_bio.id, photo_id=photo)
    #     db.add(new_photo)
    # await db.commit()
    return db_item

# --- USER FEATURES ---    
async def add_id_to_user_items_search_id_list(db: AsyncSession, user_id, item_id):
    stmt = select(User).filter(User.user_id == user_id)
    result = await db.execute(stmt)
    user: User = result.scalars().first()
    search_ids = user.get_items_search_id_list()
    search_ids.append(item_id)
    stmt = update(User).filter(User.user_id == user_id).values(items_search_id_list = search_ids).values(items_search_id = item_id)
    res = await db.execute(stmt)
    await db.commit()
    return res

# async def update_my_search_id(db: AsyncSession, my_bio_id, new_search_id):
#     print('id to be updated', new_search_id)
#     stmt = update(Bio).filter(Bio.id == my_bio_id).values(search_id=new_search_id)
#     res = await db.execute(stmt)
#     await db.commit()
#     return res

async def update_my_sales_city_search(db: AsyncSession, my_id, new_sales_city_search: bool):
    # await db.execute(update(Bio).filter(Bio.id == my_bio_id).values(search_id=new_search_id))
    # return True
    print('id to be updated', new_sales_city_search)
    stmt = update(User).filter(User.user_id == my_id).values(items_city_search=new_sales_city_search)
    res = await db.execute(stmt)
    await db.commit()
    return res


# --- HANDLE SEARCH ---
async def get_next_item_with_city(db: AsyncSession, exclude_item_ids: list, city: str):
    if exclude_item_ids is None:
        exclude_item_ids = []
    # Query items excluding those in the exclude_item_ids list and filtering by city
    stmt = (
        select(SaleItem)
        .filter(SaleItem.id.notin_(exclude_item_ids), SaleItem.city == city)
        .order_by(SaleItem.id)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()  # Ensure unique items are returned
    if items:
        # Randomly choose one item from the list
        item = random.choice(items)
        await db.refresh(item, attribute_names=["photos"])
        return item, item.photos
    return None, None

async def get_next_item_without_city(db: AsyncSession, exclude_item_ids: list, city: str):
    if exclude_item_ids is None:
        exclude_item_ids = []
    # Query items excluding those in the exclude_item_ids list and filtering by city
    stmt = (
        select(SaleItem)
        .filter(SaleItem.id.notin_(exclude_item_ids), SaleItem.city != city)
        .order_by(SaleItem.id)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()  # Ensure unique items are returned
    if items:
        # Randomly choose one item from the list
        item = random.choice(items)
        await db.refresh(item, attribute_names=["photos"])
        return item, item.photos
    return None, None


# # --- HANDLE NEXT ---
# async def like_user(db: AsyncSession, bio_id: int, liked_bio_id: int):
#     existing_like_stmt = select(Like).filter(Like.bio_id == bio_id, Like.liked_bio_id == liked_bio_id)
#     existing_like_result = await db.execute(existing_like_stmt)
#     existing_like = existing_like_result.scalars().first()
#     if not existing_like:
#         new_like = Like(bio_id=bio_id, liked_bio_id=liked_bio_id)
#         db.add(new_like)
#         await db.commit()
#         await db.refresh(new_like)

#         reciprocal_like_stmt = select(Like).filter(Like.bio_id==liked_bio_id, Like.liked_bio_id==bio_id)
#         reciprocal_like_result = await db.execute(reciprocal_like_stmt)
#         reciprocal_like = reciprocal_like_result.scalars().first()

#         if reciprocal_like:
#             update_stmt = (update(Like).where(Like.bio_id==bio_id, Like.liked_bio_id==liked_bio_id)
#                            .values(is_match=True))
#             await db.execute(update_stmt)

#             update_reciprocal_stmt = (
#                 update(Like).
#                 where(Like.bio_id==liked_bio_id, Like.liked_bio_id==bio_id).
#                 values(is_match=True)
#             )
#             await db.execute(update_reciprocal_stmt)

#             await db.commit()
#             return True
#     return False
# async def get_bio_by_id(db: AsyncSession, bio_id: int):
#     stmt = select(Bio).options(joinedload(Bio.photos)).filter(Bio.id == bio_id).order_by(Bio.id).limit(1)
#     result = await db.execute(stmt)
#     bio = result.scalars().first()
#     photos = []
#     if bio:
#         photos = bio.photos
#     return bio, photos









# async def get_match_for_bio(db: AsyncSession, bio_id: int):
#     match_stmt = select(Like).options(joinedload(Like.liked_bio)).filter(Like.bio_id == bio_id)
#     match_result = await db.execute(match_stmt)
#     match = match_result.scalars().first()
#     matched_user = match.liked_bio
#     return matched_user

async def get_test(db: AsyncSession):
    result = await db.execute(select(Bio).filter(Bio.user_id == 5479352761))
    return result.scalars().first()

