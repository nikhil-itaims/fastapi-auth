from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from app.routers import auth_router
from app.database import engine
from app.models import Base

app = FastAPI()

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.client_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=['Auth'], prefix='/api/auth')

Base.metadata.create_all(bind=engine)

@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI"}
