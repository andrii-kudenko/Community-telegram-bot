from typing import List
import random
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, BigInteger, Boolean, JSON

DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/bot1"

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    city: Mapped[str] = mapped_column(String(25), nullable=True)

    jobs_search_id: Mapped[int] = mapped_column(default=0)
    jobs_search_id_list: Mapped[list] = mapped_column(JSON, default=lambda: [])
    jobs_city_search: Mapped[bool] = mapped_column(Boolean, default=True)
    
    items_search_id: Mapped[int] = mapped_column(default=0)
    items_search_id_list: Mapped[list] = mapped_column(JSON, default=lambda: [])
    items_city_search: Mapped[bool] = mapped_column(Boolean, default=True)

    livings_search_id: Mapped[int] = mapped_column(default=0)
    livings_search_id_list: Mapped[list] = mapped_column(JSON, default=lambda: [])
    livings_city_search: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    bio: Mapped["Bio"] = relationship(back_populates="user", uselist=False)
    jobs: Mapped[List["Job"]] = relationship(back_populates="user", cascade="all, delete-orphan", foreign_keys='Job.user_id')
    user_applications: Mapped[List["JobApplication"]] = relationship(back_populates="applicant_user", cascade="all, delete-orphan", foreign_keys='JobApplication.applicant_user_id')
    sale_items: Mapped[List["SaleItem"]] = relationship(back_populates="user", cascade="all, delete-orphan", foreign_keys='SaleItem.user_id')
    livings: Mapped[List["Living"]] = relationship(back_populates="user", cascade="all, delete-orphan", foreign_keys='Living.user_id')

    def get_jobs_search_id_list(self):
        return self.jobs_search_id_list
    def get_items_search_id_list(self):
        return self.items_search_id_list
    def get_livings_search_id_list(self):
        return self.livings_search_id_list

    def set_jobs_search_id_list(self, numbers):
        self.number_list = numbers

    # TRY TO ADD NEW ID THROUGH A METHOD !!!
    
    # def add_number_to_jobs_search_id_list(self, number):
    #     if self.jobs_search_id_list is None:
    #         self.jobs_search_id_list = []
    #     self.jobs_search_id_list.append(number)

    def get_items_search_id_list(self):
        return self.items_search_id_list

    # def generate_unique_random_jobs_search_id(self, min_value=1, max_value=100):
    #     existing_numbers = self.get_jobs_search_id_list()
    #     while True:
    #         rand_number = random.randint(min_value, max_value)
    #         if rand_number not in existing_numbers:
    #             return rand_number


class Bio(Base):
    __tablename__ = 'bios'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.user_id'), unique=True, nullable=False, index=True) 
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
    bio_id: Mapped[int] = mapped_column(Integer, ForeignKey('bios.id'), nullable=False)
    photo_id: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped["Bio"] = relationship(back_populates="photos", foreign_keys=[bio_id])

class Like(Base):
    __tablename__ = 'likes'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bio_id: Mapped[int] = mapped_column(ForeignKey('bios.id'), nullable=False)
    liked_bio_id: Mapped[int] = mapped_column(ForeignKey('bios.id'), nullable=False)
    is_match: Mapped[Boolean] = mapped_column(Boolean, default=False)
    bio: Mapped["Bio"] = relationship(back_populates="likes", foreign_keys=[bio_id])
    liked_bio: Mapped["Bio"] = relationship(back_populates="liked_by", foreign_keys=[liked_bio_id])


class Job(Base):
    __tablename__ = 'jobs'
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey('users.user_id'), nullable=False, index=True) 
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    skills: Mapped[str] = mapped_column(String(255), nullable=False)  # Store skills as a comma-separated string
    # location = mapped_column(String, nullable=False)
    latitude: Mapped[str] = mapped_column(String(15))
    longtitude: Mapped[str] = mapped_column(String(15))
    city: Mapped[str] = mapped_column(String(40))
    address: Mapped[str] = mapped_column(String(40))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="jobs", foreign_keys=[user_id])  
    job_applications: Mapped[List["JobApplication"]] = relationship(back_populates="job", cascade="all, delete-orphan", foreign_keys='JobApplication.job_id')
    
    def get_skills(self):
        return self.skills.split(",")  # Convert comma-separated string back to list
    
class JobApplication(Base):
    __tablename__ = 'jobs_applications'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey('jobs.id'), nullable=False)
    applicant_user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    
    # Relationships
    job: Mapped["Job"] = relationship(back_populates="job_applications", foreign_keys=[job_id])
    applicant_user: Mapped["User"] = relationship(back_populates="user_applications", foreign_keys=[applicant_user_id])


class SaleItem(Base):
    __tablename__ = 'sale_items'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.user_id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[str] = mapped_column(String(10), nullable=True)
    city: Mapped[str] = mapped_column(String(50))
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    user: Mapped["User"] = relationship(back_populates="sale_items")
    photos: Mapped[List["SaleItemPhoto"]] = relationship(back_populates="sale_item", cascade="all, delete-orphan")

class SaleItemPhoto(Base):
    __tablename__ = 'sale_items_photos'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sale_item_id: Mapped[int] = mapped_column(ForeignKey('sale_items.id'), nullable=False)
    photo_id: Mapped[str] = mapped_column(String(100), nullable=False)
    sale_item: Mapped["SaleItem"] = relationship(back_populates="photos", foreign_keys=[sale_item_id])


class Living(Base):
    __tablename__ = 'livings'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.user_id'), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[str] = mapped_column(String(10), nullable=True)
    city: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(50), nullable=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    user: Mapped["User"] = relationship(back_populates="livings")
    photos: Mapped[List["LivingPhoto"]] = relationship(back_populates="living", cascade="all, delete-orphan")
    

class LivingPhoto(Base):
    __tablename__ = 'livings_photos'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    living_id: Mapped[int] = mapped_column(ForeignKey('livings.id'), nullable=False)
    photo_id: Mapped[str] = mapped_column(String(100), nullable=False)
    living: Mapped["Living"] = relationship(back_populates="photos", foreign_keys=[living_id])

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)