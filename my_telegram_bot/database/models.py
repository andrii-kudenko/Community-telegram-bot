from typing import List
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, BigInteger, Boolean

DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/bot1"

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(25), nullable=True)
    bio = relationship("Bio", back_populates="user", uselist=False)
    jobs = relationship("Job", back_populates="user")

class Bio(Base):
    __tablename__ = 'bios'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey('users.user_id'), unique=True, nullable=False, index=True) 
    profile_name: Mapped[str] = mapped_column(String(25))
    profile_bio: Mapped[str] = mapped_column(String(255))
    profile_age: Mapped[int] = mapped_column()
    latitude: Mapped[str] = mapped_column(String(15))
    longtitude: Mapped[str] = mapped_column(String(15))
    profile_city: Mapped[str] = mapped_column(String(50))
    search_id: Mapped[int] = mapped_column(Integer)
    beyond_city_search_id: Mapped[int] = mapped_column(Integer)
    city_search: Mapped[Boolean] = mapped_column(Boolean, default=True)
    user = relationship("User", back_populates="bio", uselist=False)
    photos: Mapped[List["BioPhoto"]] = relationship(back_populates="bio", cascade="all, delete-orphan")
    likes: Mapped["Like"] = relationship(back_populates="bio", cascade="all, delete-orphan", foreign_keys='Like.bio_id')
    liked_by: Mapped["Like"] = relationship(back_populates="liked_bio", cascade="all, delete-orphan", foreign_keys='Like.liked_bio_id')

class BioPhoto(Base):
    __tablename__ = 'bios_photos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bio_id: Mapped[int] = mapped_column(Integer, ForeignKey('bios.id'), nullable=True)
    photo_id: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped["Bio"] = relationship(back_populates="photos")

class Like(Base):
    __tablename__ = 'likes'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bio_id: Mapped[int] = mapped_column(ForeignKey('bios.id'), nullable=False)
    liked_bio_id: Mapped[int] = mapped_column(ForeignKey('bios.id'), nullable=False)
    is_match: Mapped[Boolean] = mapped_column(Boolean, default=False)
    bio: Mapped["Bio"] = relationship(back_populates="likes", foreign_keys=[bio_id])
    liked_bio: Mapped["Bio"] = relationship(back_populates="liked_by", foreign_keys=[liked_bio_id])


engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)