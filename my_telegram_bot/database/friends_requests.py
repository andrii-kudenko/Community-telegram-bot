from sqlalchemy.future import select
from sqlalchemy import BigInteger, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Bio, BioPhoto, Like
from rapidfuzz import process
from langdetect import detect


# --- HANDLE PHOTOS ---
async def add_photos_to_bio(db: AsyncSession, bio_id: int, photos: list):
    print("IM IN ADDING PHOTOS")
    for photo in photos:
        new_photo = BioPhoto(bio_id=bio_id, photo_id=photo)
        db.add(new_photo)
    await db.commit()
async def remove_existing_photos(db: AsyncSession, existing_bio: Bio):
    print("IM IN REMOVING PHOTOS")
    await db.refresh(existing_bio)
    for photo in existing_bio.photos:
        await db.delete(photo)
    await db.commit()


# --- HANDLE MY BIO ---
async def add_bio_to_user_by_id(db: AsyncSession, bio, photos):
    result = await db.execute(select(Bio).options(joinedload(Bio.photos)).filter(Bio.user_id == bio.user_id))
    existing_bio = result.scalars().first()
    if existing_bio is None:
        print("THE USER IS NONE", existing_bio)
        # db_bio = Bio(user_id=bio.user_id, profile_name=bio.profile_name, profile_bio=bio.profile_bio, profile_age=int(bio.profile_age), 
        #              profile_city=bio.profile_city, latitude=str(bio.latitude), 
        #              longtitude=str(bio.longtitude)) if bio.coordinates else Bio(user_id=bio.user_id, profile_name=bio.profile_name, 
        #                                                                          profile_bio=bio.profile_bio, 
        #                                                                     profile_age=int(bio.profile_age), profile_city=bio.profile_city, latitude='0', longtitude='0')
        db_bio = Bio(
            user_id=bio.user_id,
            profile_name=bio.profile_name,
            profile_bio=bio.profile_bio,
            profile_age=int(bio.profile_age),
            profile_city=(bio.profile_city),
            latitude=str(bio.latitude) if bio.coordinates else '0',
            longtitude=str(bio.longtitude) if bio.coordinates else '0',
            search_id = 0,
            beyond_city_search_id = 0 
        )
        db.add(db_bio)
        await db.commit()
        await db.refresh(db_bio)
        await add_photos_to_bio(db, db_bio.id, photos)
        return db_bio
    else:
        print("THE USER EXISTS", existing_bio)
        await remove_existing_photos(db, existing_bio)
        existing_bio.profile_name = bio.profile_name
        existing_bio.profile_bio = bio.profile_bio
        existing_bio.profile_age = int(bio.profile_age)
        if bio.coordinates:
            existing_bio.latitude = str(bio.latitude)
            existing_bio.longtitude = str(bio.longtitude)
        else:
            existing_bio.profile_city = bio.profile_city
        existing_bio.search_id = 0
        existing_bio.beyond_city_search_id = 0
        await db.commit()
        await db.refresh(existing_bio)
        await add_photos_to_bio(db, existing_bio.id, photos)
        return existing_bio
async def get_my_bio_by_user_id(db: AsyncSession, user_id: BigInteger): #Eventually'd be replaced by functions below (delete)
    result = await db.execute(select(Bio).options(joinedload(Bio.photos)).filter(Bio.user_id == user_id))
    my_bio = result.scalars().first()
    photos = []
    if my_bio:
        photos = my_bio.photos
    return my_bio, photos
async def get_my_bio_by_user_id_with_photos(db: AsyncSession, user_id: BigInteger):
    result = await db.execute(select(Bio).options(joinedload(Bio.photos)).filter(Bio.user_id == user_id))
    my_bio = result.scalars().first()
    photos = []
    if my_bio:
        photos = my_bio.photos
    return my_bio, photos
async def get_my_bio_by_user_id_without_photos(db: AsyncSession, user_id: BigInteger):
    result = await db.execute(select(Bio).filter(Bio.user_id == user_id))
    my_bio = result.scalars().first()
    return my_bio
async def update_my_search_id(db: AsyncSession, my_bio_id, new_search_id):
    print('id to be updated', new_search_id)
    stmt = update(Bio).filter(Bio.id == my_bio_id).values(search_id=new_search_id)
    res = await db.execute(stmt)
    await db.commit()
    return res
async def update_my_beyond_city_search_id(db: AsyncSession, my_bio_id, new_search_id):
    print('id to be updated', new_search_id)
    stmt = update(Bio).filter(Bio.id == my_bio_id).values(beyond_city_search_id=new_search_id)
    res = await db.execute(stmt)
    await db.commit()
    return res
async def update_my_city_search(db: AsyncSession, my_bio_id, new_city_search: bool):
    # await db.execute(update(Bio).filter(Bio.id == my_bio_id).values(search_id=new_search_id))
    # return True
    print('id to be updated', new_city_search)
    stmt = update(Bio).filter(Bio.id == my_bio_id).values(city_search=new_city_search)
    res = await db.execute(stmt)
    await db.commit()
    return res
# NOT USED
async def get_my_bio_id_search_id_city(db: AsyncSession, telegram_user_id: BigInteger):
    result = await db.execute(select(Bio).filter(Bio.user_id == telegram_user_id))
    my_bio = result.scalars().first()
    return my_bio.id, my_bio.search_id, my_bio.profile_city


# --- HANDLE SEARCH ---
async def get_next_bio_by_id_with_city_old(db: AsyncSession, bio_id: int, exclude_bio_id: int, city: str): # Add a calculator to calculate distances
    cities = [city.strip().lower()]
    stmt = select(Bio).options(joinedload(Bio.photos)).filter(Bio.id > bio_id).filter(Bio.id != exclude_bio_id).filter(Bio.profile_city.in_(cities)).order_by(Bio.id).limit(1)
    result = await db.execute(stmt)
    bio = result.scalars().first()
    photos = []
    if bio:
        photos = bio.photos
    return bio, photos
async def get_next_bio_by_id_with_city(db: AsyncSession, bio_id: int, exclude_bio_id: int, city: str):
    stmt = select(Bio).options(joinedload(Bio.photos)).filter(Bio.id > bio_id).filter(Bio.id != exclude_bio_id).filter(Bio.profile_city == city).order_by(Bio.id).limit(1)
    result = await db.execute(stmt)
    bio = result.scalars().first()
    photos = []
    if bio:
        photos = bio.photos
        return bio, photos
    else:
        # Detect the language of the input city name
        detected_language = detect(city)

        # Get all bios from the Bio table for fuzzy matching
        all_bios_stmt = select(Bio.profile_city).filter(Bio.id > bio_id).filter(Bio.id != exclude_bio_id)
        all_bios_result = await db.execute(all_bios_stmt)
        all_cities = all_bios_result.scalars().all()

        matched_city = None

        if all_cities:
            # Conditional logic for matching based on detected language
            if detected_language == 'ru':  # Russian
                matched_city, _, _ = process.extractOne(city, all_cities)
            else:  # Assuming input is in English or other Latin-based languages
                matched_city, _, _ = process.extractOne(city, all_cities)

            stmt = select(Bio).options(joinedload(Bio.photos)).filter(Bio.id > bio_id).filter(Bio.id != exclude_bio_id).filter(Bio.profile_city == matched_city).order_by(Bio.id).limit(1)
            result = await db.execute(stmt)
            bio = result.scalars().first()
            photos = []
            if bio:
                photos = bio.photos
                return bio, photos
        else:
            return None, []

    

    return bio, photos
async def get_next_bio_by_id_without_city(db: AsyncSession, bio_id: int, exclude_bio_id: int, city: str): # Add a calculator to calculate distances
    cities = [city.strip().lower()]
    stmt = select(Bio).options(joinedload(Bio.photos)).filter(Bio.id > bio_id).filter(Bio.id != exclude_bio_id).filter(Bio.profile_city != city).order_by(Bio.id).limit(1)
    result = await db.execute(stmt)
    bio = result.scalars().first()
    photos = []
    if bio:
        photos = bio.photos
    return bio, photos
# NOT USED
async def get_next_bio_by_id(db: AsyncSession, bio_id: int, exclude_bio_id: int):
    stmt = select(Bio).options(joinedload(Bio.photos)).filter(Bio.id > bio_id).filter(Bio.id != exclude_bio_id).order_by(Bio.id).limit(1)
    result = await db.execute(stmt)
    bio = result.scalars().first()
    photos = []
    if bio:
        photos = bio.photos
    return bio, photos


# --- HANDLE LIKE ---
async def like_user(db: AsyncSession, bio_id: int, liked_bio_id: int):
    existing_like_stmt = select(Like).filter(Like.bio_id == bio_id, Like.liked_bio_id == liked_bio_id)
    existing_like_result = await db.execute(existing_like_stmt)
    existing_like = existing_like_result.scalars().first()
    if not existing_like:
        new_like = Like(bio_id=bio_id, liked_bio_id=liked_bio_id)
        db.add(new_like)
        await db.commit()
        await db.refresh(new_like)

        reciprocal_like_stmt = select(Like).filter(Like.bio_id==liked_bio_id, Like.liked_bio_id==bio_id)
        reciprocal_like_result = await db.execute(reciprocal_like_stmt)
        reciprocal_like = reciprocal_like_result.scalars().first()

        if reciprocal_like:
            update_stmt = (update(Like).where(Like.bio_id==bio_id, Like.liked_bio_id==liked_bio_id)
                           .values(is_match=True))
            await db.execute(update_stmt)
            update_reciprocal_stmt = (
                update(Like).
                where(Like.bio_id==liked_bio_id, Like.liked_bio_id==bio_id).
                values(is_match=True)
            )
            await db.execute(update_reciprocal_stmt)
            await db.commit()
            return True
    return False
async def get_bio_by_id(db: AsyncSession, bio_id: int):
    stmt = select(Bio).options(joinedload(Bio.photos)).filter(Bio.id == bio_id).order_by(Bio.id).limit(1)
    result = await db.execute(stmt)
    bio = result.scalars().first()
    photos = []
    if bio:
        photos = bio.photos
    return bio, photos
# END




















# async def get_match_for_bio(db: AsyncSession, bio_id: int):
#     match_stmt = select(Like).options(joinedload(Like.liked_bio)).filter(Like.bio_id == bio_id)
#     match_result = await db.execute(match_stmt)
#     match = match_result.scalars().first()
#     matched_user = match.liked_bio
#     return matched_user

# async def get_test(db: AsyncSession):
#     result = await db.execute(select(Bio).filter(Bio.user_id == 5479352761))
#     return result.scalars().first()

