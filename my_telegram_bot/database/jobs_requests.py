from sqlalchemy.future import select
from sqlalchemy import BigInteger, update, func, delete
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Job, JobApplication, Resume
import random
from langdetect import detect
from rapidfuzz import process
from transliterate import translit


# --- USER ---
async def get_user(db: AsyncSession, user_id: BigInteger):
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()
    return user


# ---SEARCH---
async def get_next_job_by_id(db: AsyncSession, exclude_job_ids: list):
    stmt = select(Job).filter(Job.id.notin_(exclude_job_ids)).order_by(Job.id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    if jobs:
        job = random.choice(jobs)
        return job
    else:
        return None
    
async def get_next_job_by_id_with_city_old(db: AsyncSession, exclude_job_ids: list, city: str, user_id: BigInteger):
    stmt = select(Job).filter(Job.id.notin_(exclude_job_ids)).filter(Job.user_id != user_id).filter(Job.city == city).order_by(Job.id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    if jobs:
        job = random.choice(jobs)
        return job
    else:
        return None
async def get_next_job_by_id_with_city(db: AsyncSession, exclude_job_ids: list, city: str, user_id: BigInteger):
    stmt = select(Job).filter(Job.id.notin_(exclude_job_ids)).filter(Job.user_id != user_id).filter(Job.city == city).order_by(Job.id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    if jobs:
        job = random.choice(jobs)
        return job
    else:
        # Detect the language of the input city name
        detected_language = detect(city)
        # Get all cities from the Job table for fuzzy matching
        all_jobs_stmt = select(Job.city).filter(Job.id.notin_(exclude_job_ids)).filter(Job.user_id != user_id)
        all_cities_result = await db.execute(all_jobs_stmt)
        all_cities = all_cities_result.scalars().all()
        matched_city = None
        if all_cities: 
            # Conditional logic for matching based on detected language
            if detected_language == 'ru':  # Russian
                # Use fuzzy matching directly with the original city
                matched_city, _, _ = process.extractOne(city, all_cities)
            else:  # Assuming input is in English or other Latin-based languages
                matched_city, _, _ = process.extractOne(city, all_cities)

                # Now filter jobs based on the matched city
            stmt = select(Job).filter(Job.id.notin_(exclude_job_ids)).filter(Job.user_id != user_id).filter(Job.city == matched_city).order_by(Job.id)
            result = await db.execute(stmt)
            jobs = result.scalars().all()
            
            if jobs:
                job = random.choice(jobs)
                return job
            else:
                return None
        else:
            return None
    
async def get_next_job_by_id_without_city(db: AsyncSession, exclude_job_ids: list, city: str, user_id: BigInteger):
    stmt = select(Job).filter(Job.id.notin_(exclude_job_ids)).filter(Job.user_id != user_id).filter(Job.city != city).order_by(Job.id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    if jobs:
        job = random.choice(jobs)
        return job
    else:
        return None



# --- HANDLE JOBS ---
async def get_job_by_id(db: AsyncSession, job_id: int):
    stmt = select(Job).filter(Job.id == job_id).order_by(Job.id)
    result = await db.execute(stmt)
    job = result.scalars().one()
    if job:
        return job
    else:
        return None
async def get_applicants_by_job_id(db: AsyncSession, job_id):
    stmt = select(JobApplication).filter(JobApplication.job_id == job_id).options(joinedload(JobApplication.applicant_resume)).order_by(JobApplication.id)
    result = await db.execute(stmt)
    job_applications = result.scalars().all()
    applicants = []
    for application in job_applications:
        applicants.append(application.applicant_resume)
    return applicants
async def delete_related_job_applications(db: AsyncSession, job_id: int):
    stmt = delete(JobApplication).where(JobApplication.job_id == job_id)
    await db.execute(stmt)
    await db.commit()
async def delete_job_by_id(db: AsyncSession, job_id: int):
    await delete_related_job_applications(db, job_id)
    stmt = delete(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    await db.commit()
    return result
async def add_job_post_to_user(db: AsyncSession, job):
    print(job.city)
    db_job = Job(user_id=job.user_id, title=job.title, description=job.description, skills=job.skills,
                 latitude=str(job.latitude),
                 longtitude=str(job.longtitude),
                 city=job.city, address=job.address)
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job
# async def add_job_post_to_user(db: AsyncSession, job):
#     db_job = Job(user_id=job.user_id, title=job.title, description=job.description, skills=job.skills,
#                  latitude=str(job.latitude) if job.coordinates else '0',
#                  longtitude=str(job.longtitude) if job.coordinates else '0',
#                  city=job.city, address=job.address)
#     db.add(db_job)
#     await db.commit()
#     await db.refresh(db_job)
#     return db_job
async def test_add_job_post_to_user(db: AsyncSession):
    db_job = Job(user_id=539444135, title='Fashion Consultant', description='We hire a professional fashion designer/stylist', skills='Communicate with customers, look for appropriate clothes as per customer request',
                 latitude=str(43.468128),
                 longtitude=str(-79.697358),
                 city='Oakville', address='Oakville')
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job
async def update_job_by_id(db: AsyncSession, job_id: int, field, field_value: str):
    stmt = update(Job).where(Job.id == job_id).values({field: field_value})
    result = await db.execute(stmt)
    await db.commit()
    return result
async def get_user_jobs(db: AsyncSession, user_id):
    stmt = select(Job).filter(Job.user_id == user_id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return jobs


# --- USER FEATURES ---
async def add_id_to_user_jobs_search_id_list(db: AsyncSession, user_id, job_id):
    stmt = select(User).filter(User.user_id == user_id)
    result = await db.execute(stmt)
    user: User = result.scalars().first()
    search_ids = user.get_jobs_search_id_list()
    search_ids.append(job_id)
    stmt = update(User).filter(User.user_id == user_id).values(jobs_search_id_list = search_ids).values(jobs_search_id = job_id)
    res = await db.execute(stmt)
    await db.commit()
    return res
async def apply_for_job(db: AsyncSession, job_id, applicant_user_id):
    stmt = select(Resume).where(Resume.user_id == applicant_user_id)
    result = await db.execute(stmt)
    resume = result.scalars().first()
    job_application = JobApplication(job_id=job_id, applicant_resume_id=resume.id)
    db.add(job_application)
    await db.commit()
    await db.refresh(job_application)
    return job_application
async def apply_for_job_by_resume_id(db: AsyncSession, job_id, applicant_resume_id):
    job_application = JobApplication(job_id=job_id, applicant_user_id=applicant_resume_id)
    db.add(job_application)
    await db.commit()
    await db.refresh(job_application)
    return job_application
# async def update_user_jobs_search_id_list(db: AsyncSession, user_id):
#     numbers = [1, 2, 3, 4, 5]
#     stmt = select(User).filter(User.user_id == user_id)
#     result = await db.execute(stmt)
#     user = result.scalars().first()
#     user.set_jobs_search_id_list(numbers)
#     await db.commit()
#     await db.refresh(user)
#     return user
async def update_my_jobs_city_search(db: AsyncSession, my_id, new_jobs_city_search: bool):
    print('id to be updated', new_jobs_city_search)
    stmt = update(User).filter(User.user_id == my_id).values(jobs_city_search=new_jobs_city_search)
    res = await db.execute(stmt)
    await db.commit()
    return res
async def check_for_resume(db: AsyncSession, user_id: BigInteger):
    stmt = select(Resume).where(Resume.user_id == user_id)
    result = await db.execute(stmt)
    resume = result.scalars().first()
    print(resume.full_name, resume.additional_information, resume.email_address)
    # return resume.check_for_valid_resume()
    if resume and resume.check_for_valid_resume(): return True
    else: return False
    # return True

async def get_user_resume(db: AsyncSession, resume_id: int):
    stmt = select(Resume).where(Resume.id == resume_id)
    result = await db.execute(stmt)
    resume = result.scalars().first()
    return resume

# END




















# async def get_next_job_by_id(db: AsyncSession, job_id: int, exclude_job_ids: list):
#     stmt = select(func.count(Job.id))
#     result = await db.execute(stmt)
#     row_count = result.scalar()
#     new_number = generate_unique_random_jobs_search_id(exclude_job_ids, min_value=0, max_value=row_count)
#     stmt = select(Job).filter(Job.id > job_id, Job.id.notin_(exclude_job_ids)).order_by(Job.id).limit(1)
#     result = await db.execute(stmt)
#     job = result.scalars().first()
#     if job is None:
#         stmt = select(Job).filter(Job.id < job_id).order_by(Job.id).limit(1)
#         result = await db.execute(stmt)
#         job2 = result.scalars().first()
#         return job2
#     return job


    # stmt = update(Bio).filter(Bio.id == my_bio_id).values(city_search=new_city_search)
    # res = await db.execute(stmt)
    # await db.commit()
# async def get_row_count():
#     async with AsyncSessionLocal() as session:
#         stmt = select(func.count(Job.id))
#         result = await session.execute(stmt)
#         row_count = result.scalar()
#         return row_count

def generate_unique_random_jobs_search_id(existing_numbers, min_value, max_value):
    while True:
        rand_number = random.randint(min_value, max_value)
        if rand_number not in existing_numbers:
            return rand_number