from database import User
from bson import ObjectId
from config import logger

async def add_user(data: dict):
    try:
        user = User.insert_one(data)
        return str(user.inserted_id)

    except Exception as e:
        logger.error(str(e))
        return None

async def get_user_by_email(email: str):
    try:
        user = User.find_one({"email": email})
        return user

    except Exception as e:
        logger.error(str(e))
        return None
    
async def get_user_by_id(user_id: str):
    try:
        user = User.find_one({"_id": ObjectId(user_id)})
        return user

    except Exception as e:
        logger.error(str(e))
        return None

async def update_user_details(user_id: str, data: dict):
    try:
        user = User.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        return user_id

    except Exception as e:
        logger.error(str(e))
        return None

async def get_all_users():
    try:
        users = list(User.find())
        return users

    except Exception as e:
        logger.error(str(e))
        return None

