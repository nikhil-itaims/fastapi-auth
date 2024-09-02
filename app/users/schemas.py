from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from helpers import constants
import re

class RegisterSchema(BaseModel):
    first_name: str = Field()
    last_name: str = Field()
    email: str = Field(pattern=constants.email_regex)
    phone: str = Field(min_length=10, max_length=10)
    country_code: str = Field(max_length=3) 
    password: str = Field(min_length=8, max_length=16)
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    @field_validator('email')
    def validate_pan_number(cls, value):
        if not re.match(constants.email_regex, value):
            raise ValueError("Invalid email address")
        return value
    
    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase character.")

        symbols = "!@#$%^&*()_-+=<>?"
        if not any(c in symbols for c in value):
            raise ValueError("Password must contain at least one symbol.")
        
        numbers = "0123456789"
        if not any(c in numbers for c in numbers):
            raise ValueError("Password must contain at least one number.")

        return value

class LoginSchema(BaseModel):
    email: str = Field()
    password: str = Field()

class ForgotPasswordRequestSchema(BaseModel):
    email: str = Field()

class ResetForgotPasswordSchema(BaseModel):
    secret_token: str = Field()
    new_password: str = Field()
    confirm_password: str = Field()

class ChangePasswordSchema(BaseModel):
    current_password: str = Field()
    new_password: str = Field()
    confirm_password: str = Field()