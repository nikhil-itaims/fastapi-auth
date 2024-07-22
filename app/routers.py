from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
import re
from app.models import User
from app.utils import create_access_token, create_refresh_token, get_current_user, get_password_hash, verify_password
from app.schemas import CreateUserSchema, LoginUserSchema, UserSchema
from app.repository import create_user, get_user_by_email
from app.database import get_db

auth_router = APIRouter()

@auth_router.post('/register')
async def register(payload: CreateUserSchema, db: Session = Depends(get_db)):
    try:
        user_data = payload.dict()
        user_data['email'] = payload.email.lower()

        exists_user = get_user_by_email(db, user_data['email'])

        if exists_user:
            return {"success": False, "status_code": 400, "message": "User with this email already exists", "data": None}
        
        user_data['password'] = get_password_hash(payload.password)

        user = UserSchema(**user_data)
        db_user = create_user(db, user)

        if db_user:
            return {"success": True, "status_code": 201, "message": "User created successfully", "data": {"user_id": db_user.id}}
        else:
            return {"success": False, "status_code": 500, "message": "Something Went Wrong. Please Try Again", "data": None}
    
    except Exception as e:
        return {"status_code": 500, 'status': 'fail', "message":"Something Went Wrong. Please Try Again", "error_message": str(e)}

@auth_router.post('/login')
def login(payload: LoginUserSchema, db: Session = Depends(get_db)):
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(regex, payload.email.lower())):
            user = get_user_by_email(db, payload.email)

            if not user:
                return {"success": False, "status_code": 400, "message": "User with this email not exists", "data": None}
            
            if payload.email != user.email:
                return {'status': 'fail','status_code': 409,'message':'Incorrect email'}
            
            if not verify_password(payload.password, user.password):
                return {'status': 'fail','status_code': 409,'message':'Incorrect Password'}
        
            user_payload = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            
            access_token = create_access_token(user_payload)
            refresh_token = create_refresh_token(user_payload)
            
            user_payload['access_token'] = access_token
            user_payload['refresh_token'] = refresh_token
        
            return {'status_code': 200,'status': 'success', "message":"You are successfully logged in", 'data': user_payload}
        
        else: 
            return {'status': 'fail','status_code': 404,'message': 'Please enter valid email address'}
    
    except Exception as e:
        return {"status_code": 500, 'status': 'fail', "message": "Something Went Wrong. Please Try Again", "error_message": str(e)}
    
@auth_router.get("/profile")
async def profile(current_user: User = Depends(get_current_user)):
    try:
        if current_user:
            return {"success": True, "status_code": 200, "message": "User profile", "data": current_user}
    except Exception as e:
        return {"success": False, "status_code": 400, "message": "Invalid token please login again", "error_message": str(e), "data": None}
    