from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserSchema

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserSchema):
    db_user = User(first_name=user.first_name, last_name=user.last_name, email=user.email, password=user.password, created_at=user.created_at, updated_at=user.updated_at)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
