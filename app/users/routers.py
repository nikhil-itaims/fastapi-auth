from fastapi import APIRouter, status, Depends, BackgroundTasks, Depends
from helpers.response import Response
from app.users.messages import ErrorMessage, InfoMessage
from app.users.schemas import RegisterSchema, LoginSchema, ForgotPasswordRequestSchema, \
    ResetForgotPasswordSchema, ChangePasswordSchema
from app.users.models import User
from fastapi.security import OAuth2PasswordRequestForm
from app.users.repository import add_user, get_user_by_email, get_user_by_id, update_user_details
from auth import create_access_token, create_refresh_token, get_current_user, get_password_hash, verify_password
import re 
from config import logger, get_settings
import time
from helpers import send_email, constants
import jwt

settings = get_settings()

auth_router = APIRouter()

@auth_router.post("/register")
async def register(payload: RegisterSchema):
    try:
        payload = payload.dict()
        payload['email'] = payload['email'].lower()

        exists_user = await get_user_by_email(payload['email'])

        if exists_user:
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_already_exists, None)

        payload['password'] = get_password_hash(payload['password'])
        
        if not payload.get("role"):
            payload['role'] = constants.Role.owner
            
        user_data = User(**payload).dict()
        user_id = await add_user(user_data)
        if user_id:
            user_data['_id'] = user_id
            return Response.created(InfoMessage.user_created, user_data)
    
        else: return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_not_added, None)
    
    except Exception as e:
        logger.error(str(e))
        return Response.error(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, str(e))

@auth_router.post('/login')
async def login(payload: LoginSchema):
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(regex, payload.email.lower())):
            user = await get_user_by_email(payload.email)

            if not user:
                return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_email_not_exists, None)
            
            if payload.email != user['email']:
                return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.wrong_email, None)
            
            if not verify_password(payload.password, user['password']):
                return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.wrong_password, None)
        
            user_data = {
                "_id": str(user['_id']),
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "phone": user['phone']
            }
            
            access_token = create_access_token(user_data)
            refresh_token = create_refresh_token(user_data)
            
            user_data['access_token'] = access_token
            user_data['refresh_token'] = refresh_token
        
            return Response.success(InfoMessage.login_success, user_data)
        
        else: 
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.invalid_email, None)
    
    except Exception as e:
        logger.error(str(e))
        return Response.error(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, str(e))

@auth_router.post('/swagger-login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(regex, form_data.username.lower())):
            user = await get_user_by_email(form_data.username)

            if not user:
                return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_email_not_exists, None)
            
            if form_data.username != user['email']:
                return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.wrong_email, None)
            
            if not verify_password(form_data.password, user['password']):
                return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.wrong_password, None)
        
            user_data = {
                "_id": str(user['_id']),
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "phone": user['phone']
            }
            
            access_token = create_access_token(user_data)
            refresh_token = create_refresh_token(user_data)
            
            user_data['access_token'] = access_token
            user_data['refresh_token'] = refresh_token

            return {"access_token": access_token}
        
        else: 
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.invalid_email, None)
    
    except Exception as e:
        logger.error(str(e))
        return Response.error(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, str(e))

@auth_router.post('/forget-password')
async def forget_password(payload: ForgotPasswordRequestSchema, background_tasks: BackgroundTasks):
    try:
        user = await get_user_by_email(payload.email)

        if not user:
            print("user", user)
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_email_not_exists, None) 
        
        token_payload = {
            "user_id": str(user['_id']),
            "expires": time.time() + 900  # 15 mins
        }

        secret_token = create_access_token(token_payload)
        forget_url_link = f"{settings.frontend_host_url}/{settings.frontend_forget_password_url}?token={secret_token}"

        context = {
            "name": f"{user['first_name']} {user['last_name']}",
            "link_expiry_min": 15,
            "reset_link": forget_url_link
        }

        background_tasks.add_task(send_email.send, "Reset password", user['email'], "forgot_password.html", context)        
        return Response.success(InfoMessage.forgot_password_mail_sent, context)

    except Exception as e:
        logger.error(str(e))
        return Response.error(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, str(e))
    
@auth_router.post('/reset-password')
async def reset_password(payload: ResetForgotPasswordSchema):
    try:
        payload = payload.dict()
        
        try:
            decoded_payload = jwt.decode(payload['secret_token'], settings.secret_key, algorithms=[settings.oauth_algorithm])
        except:
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.forgot_password_link_expire, None)
        
        current_time = time.time()
        expiration_datetime = decoded_payload['expires']
        user_id = decoded_payload['user_id']

        if not user_id:
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.invalid_secret_token, None)

        if current_time > expiration_datetime:
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.forgot_password_link_expire, None)
    
        if payload['new_password'] != payload['confirm_password']:
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.same_not_password, None)
        
        user = await get_user_by_id(user_id)

        if verify_password(payload['new_password'], user['password']):
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.same_password, None)

        data = {
            "password": get_password_hash(payload['new_password'])
        }

        password_updated = await update_user_details(user_id, data)
        if password_updated:
            return Response.success(InfoMessage.password_updated, None)
        
        else:
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.password_not_updated, None)

    except Exception as e:
        logger.error(str(e))
        return Response.error(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, str(e))

@auth_router.post('/change-password')
async def change_password(payload: ChangePasswordSchema, current_user: User = Depends(get_current_user)):
    try:
        payload = payload.dict()
        user_id = str(current_user['_id'])
        user = await get_user_by_id(user_id)

        if not verify_password(payload['current_password'], user['password']):
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.wrong_current_password, None)

        if payload['new_password'] != payload['confirm_password']:
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.same_not_password, None)
        
        if verify_password(payload['new_password'], user['password']):
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.same_password, None)

        data = {
            "password": get_password_hash(payload['new_password'])
        }

        password_updated = await update_user_details(user_id, data)
        if password_updated:
            return Response.success(InfoMessage.password_updated, None)
        
        else:
            return Response.error(status.HTTP_400_BAD_REQUEST, ErrorMessage.password_not_updated, None)

    except Exception as e:
        logger.error(str(e))
        return Response.error(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, str(e))
