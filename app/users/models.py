from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    _id: str | None = None
    first_name: str
    last_name: str
    email: str
    phone: str
    country_code: str
    password: str
    role: str
    created_at: datetime
    updated_at: datetime

class Profile(BaseModel):
    _id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    country_code: str
