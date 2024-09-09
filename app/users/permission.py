from helpers import global_repository
from database import User
from helpers import constants

class PermissionErrorMessage:
    not_authorized = "You are not authorized to access this feature"

async def is_admin(user_id):
    user_data = await global_repository.get_document_data(User, user_id)
    return True if user_data['role'] == constants.Role.admin else False

async def is_customer(user_id):
    user_data = await global_repository.get_document_data(User, user_id)
    return True if user_data['role'] == constants.Role.customer else False
