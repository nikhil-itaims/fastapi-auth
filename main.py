from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from app.users.routers import auth_router

settings = get_settings()

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = exc.errors()
    if 'email' in details[0]['loc']:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status_code": 422, 
                "status":"fail",
                "message": details[0]['msg'].split(",")[-1].lstrip()
            })
        )
    
    if 'password' in details[0]['loc']:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status_code": 422, 
                "status":"fail",
                "message": details[0]['msg'].split(",")[-1].lstrip()
            })
        )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.client_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=['Auth'], prefix='/api/v1/auth')

@app.get("/")
def root():
    return {"message": "Welcome to OTA backend"}
