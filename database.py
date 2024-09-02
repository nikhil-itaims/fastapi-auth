from pymongo import MongoClient
from config import get_settings
from config import logger

settings = get_settings()
client = MongoClient(settings.mongo_uri)

try:
    db = client[settings.db_name]
except Exception as e:
    logger.error(str(e))

# Define collections here
User = db.users
