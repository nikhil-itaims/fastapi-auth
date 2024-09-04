from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from config import get_settings
from helpers.response import Response

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/swagger-login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
	return pwd_context.hash(password)

def create_access_token(data: dict):
	to_encode = data.copy()
	current_time = datetime.now()
	expire = current_time + timedelta(minutes=settings.access_token_expire_minutes)
	to_encode.update({"exp": expire.timestamp()})
	encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.oauth_algorithm)
	return encoded_jwt

def create_refresh_token(data: dict):
	to_encode = data.copy()
	current_time = datetime.now()
	expire = current_time + timedelta(days=settings.refresh_token_expire_minutes)
	to_encode.update({"exp": expire.timestamp(), "refresh": True})
	encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.oauth_algorithm)
	return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
	try:
		payload = jwt.decode(token, settings.secret_key, algorithms=[settings.oauth_algorithm])
		user_id = payload.get("_id")
		if not user_id:
			return Response.error(status.HTTP_401_UNAUTHORIZED, "Please login again")
    	
		return payload
  	
	except InvalidTokenError as e:
		return Response.error(status.HTTP_401_UNAUTHORIZED, "Please login again", str(e))
