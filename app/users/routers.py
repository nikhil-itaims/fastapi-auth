from fastapi import APIRouter, status, Depends, BackgroundTasks
from helpers.response import Response
from app.users.messages import ErrorMessage, InfoMessage
from app.users.schemas import RegisterSchema, LoginSchema, ForgotPasswordRequestSchema, \
    ResetForgotPasswordSchema, ChangePasswordSchema
from app.users.models import User
from app.users.repository import add_user, get_user_by_email, get_user_by_id, update_user_details
from auth import create_access_token, create_refresh_token, get_current_user, get_password_hash, verify_password
import re 
from config import logger, get_settings
import time
from helpers import send_email
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
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_already_exists, None).make

        payload['password'] = get_password_hash(payload['password'])
        user_data = User(**payload).dict()
        user_id = await add_user(user_data)
        if user_id:
            user_data['_id'] = user_id
            return Response(status.HTTP_201_CREATED, InfoMessage.user_created, user_data).make
    
        else: return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_not_added, None).make
    
    except Exception as e:
        logger.error(str(e))
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, None).make

@auth_router.post('/login')
async def login(payload: LoginSchema):
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(regex, payload.email.lower())):
            user = await get_user_by_email(payload.email)

            if not user:
                return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_email_not_exists, None).make
            
            if payload.email != user['email']:
                return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.wrong_email, None).make
            
            if not verify_password(payload.password, user['password']):
                return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.wrong_password, None).make
        
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
        
            return Response(status.HTTP_200_OK, InfoMessage.login_success, user_data).make
        
        else: 
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.invalid_email, None).make
    
    except Exception as e:
        logger.error(str(e))
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, None).make

@auth_router.post('/forget-password')
async def forget_password(payload: ForgotPasswordRequestSchema, background_tasks: BackgroundTasks):
    try:
        user = await get_user_by_email(payload.email)

        if not user:
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.user_email_not_exists, None).make 
        
        token_payload = {
            "user_id": str(user['_id']),
            "expires": time.time() + 900  # 15 mins
        }

        secret_token = create_access_token(token_payload)
        forget_url_link = f"{settings.frontend_host_url}/{settings.frontend_forget_password_url}/{secret_token}"

        context = {
            "name": f"{user['first_name']} {user['last_name']}",
            "link_expiry_min": 15,
            "reset_link": forget_url_link
        }

        background_tasks.add_task(send_email.send, "Reset password", user['email'], "forgot_password.html", context)        
        return Response(status.HTTP_200_OK, InfoMessage.forgot_password_mail_sent, context).make

    except Exception as e:
        logger.error(str(e))
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, None).make
    
@auth_router.post('/reset-password')
async def reset_password(payload: ResetForgotPasswordSchema):
    try:
        payload = payload.dict()
        
        try:
            decoded_payload = jwt.decode(payload['secret_token'], settings.secret_key, algorithms=[settings.oauth_algorithm])
        except:
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.forgot_password_link_expire, None).make
        
        current_time = time.time()
        expiration_datetime = decoded_payload['expires']
        user_id = decoded_payload['user_id']

        if not user_id:
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.invalid_secret_token, None).make

        if current_time > expiration_datetime:
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.forgot_password_link_expire, None).make
    
        if payload['new_password'] != payload['confirm_password']:
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.same_not_password, None).make
        
        user = await get_user_by_id(user_id)

        if verify_password(payload['new_password'], user['password']):
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.same_password, None).make

        data = {
            "password": get_password_hash(payload['new_password'])
        }

        password_updated = await update_user_details(user_id, data)
        if password_updated:
            return Response(status.HTTP_200_OK, InfoMessage.password_updated, None).make
        
        else:
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.password_not_updated, None).make

    except Exception as e:
        logger.error(str(e))
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, None).make

@auth_router.post('/change-password')
async def change_password(payload: ChangePasswordSchema, current_user: User = Depends(get_current_user)):
    try:
        payload = payload.dict()
        user_id = str(current_user['_id'])
        user = await get_user_by_id(user_id)

        if verify_password(payload['current_password'], user['password']):
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.wrong_current_password, None).make

        if payload['new_password'] != payload['confirm_password']:
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.same_not_password, None).make
        
        if verify_password(payload['new_password'], user['password']):
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.same_password, None).make

        data = {
            "password": get_password_hash(payload['new_password'])
        }

        password_updated = await update_user_details(user_id, data)
        if password_updated:
            return Response(status.HTTP_200_OK, InfoMessage.password_updated, None).make
        
        else:
            return Response(status.HTTP_400_BAD_REQUEST, ErrorMessage.password_not_updated, None).make

    except Exception as e:
        logger.error(str(e))
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessage.server_error, None).make
