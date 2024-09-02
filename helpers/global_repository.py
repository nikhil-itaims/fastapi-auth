from typing import Optional
from bson import ObjectId
from config import logger

async def store_bulk_document(collection, document_data: list):
    try:
        result = collection.insert_many(document_data)
        return result
    except Exception as e:
        logger.error(str(e))
        return None

async def store_document(collection, document_data: dict):
    try:
        result = collection.insert_one(document_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(str(e))
        return None
    
async def edit_document(collection, document_id, document_data: dict):
    try:
        collection.update_one({"_id": ObjectId(document_id)}, {"$set": document_data})
        return str(document_id)
    except Exception as e:
        logger.error(str(e))
        return None

async def get_document_data(collection, document_id: Optional[str] = None):
    try:
        if document_id:
            document_data = collection.find_one({"_id": ObjectId(document_id)})
            if not document_data:
                return None
            return document_data
        else:
            all_document_data = list(collection.find())
            return all_document_data
        
    except Exception as e:
        logger.error(str(e))
        return None

async def delete_document(document, document_id):
    try:
        result = document.delete_one({"_id": ObjectId(document_id)})
        return result
    except Exception as e:
        logger.error(str(e))
        return None
    