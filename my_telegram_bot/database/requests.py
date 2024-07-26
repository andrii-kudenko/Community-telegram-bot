from sqlalchemy.future import select
from sqlalchemy import BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Bio
import logging

async def add_user(db: AsyncSession, user_id: BigInteger, name: str):
    db_user = User(user_id=user_id, name=name, city='Oakville')
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: BigInteger):
    result = await db.execute(select(User).filter(User.user_id == user_id))
    return result.scalars().first()

# rework, if user creates new bio, just create new bio in database and delete the previous one
async def add_bio_to_user_by_id(db: AsyncSession, user_id: BigInteger, name: str,
                                bio: str, age: int, latitude: str = '0', longtitude: str = '0'):
    result = await db.execute(select(Bio).filter(Bio.user_id == user_id))
    existing_bio = result.scalars().first()
    if existing_bio is None:
        db_bio = Bio(user_id=user_id, profile_name=name, profile_bio=bio, profile_age=age, latitude=latitude, longtitude=longtitude)
        db.add(db_bio)
        await db.commit()
        await db.refresh(db_bio)
        return db_bio
    else:
        existing_bio.profile_name = name
        existing_bio.profile_bio = bio
        existing_bio.profile_age = age
        existing_bio.latitude = latitude
        existing_bio.longtitude = longtitude

        await db.commit()
        await db.refresh(existing_bio)
        return existing_bio

async def get_people(db: AsyncSession, bio_id: BigInteger):
    pass

async def get_bio_by_id(db: AsyncSession, bio_id: int, exclude_bio_id: int):
    stmt = select(Bio).filter(Bio.id > bio_id).filter(Bio.id != exclude_bio_id).order_by(Bio.id).limit(1)
    result = await db.execute(stmt)
    bio = result.scalars().first()
    return bio

async def get_my_bio_by_id(db: AsyncSession, user_id: BigInteger):
    result = await db.execute(select(Bio).filter(Bio.user_id == user_id))
    return result.scalars().first()
async def get_test(db: AsyncSession):
    result = await db.execute(select(Bio).filter(Bio.user_id == 5479352761))
    return result.scalars().first()