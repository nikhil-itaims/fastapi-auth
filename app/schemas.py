from pydantic import BaseModel
from datetime import datetime

class CreateUserSchema(BaseModel):
  first_name: str
  last_name: str
  email: str
  password: str

class LoginUserSchema(BaseModel):
  email: str
  password: str

class UserSchema(BaseModel):
  first_name: str
  last_name: str
  email: str
  password: str
  created_at : datetime = datetime.now()
  updated_at : datetime = datetime.now()
