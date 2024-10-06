from sqlalchemy.future import select
from sqlalchemy import BigInteger, update, func, delete
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Resume
import random

async def get_my_resume(db: AsyncSession, user_id: BigInteger):
    stmt = select(Resume).where(Resume.user_id == user_id)
    result = await db.execute(stmt)
    resume = result.scalars().first()
    return resume

async def update_resume_by_user_id(db: AsyncSession, user_id: BigInteger, field, field_value: str):
    stmt = update(Resume).where(Resume.user_id == user_id).values({field: field_value})
    result = await db.execute(stmt)
    await db.commit()
    return result

async def create_resume(db: AsyncSession, user_id: BigInteger):
    new_resume = Resume(user_id=user_id)
    db.add(new_resume)
    await db.commit()

    stmt = select(Resume).where(Resume.user_id == user_id).order_by(Resume.id)
    result = await db.execute(stmt)
    resume = result.scalars().one()
    return resume