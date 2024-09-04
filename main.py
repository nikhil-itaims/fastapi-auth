from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings, logger
from app.users.routers import auth_router

settings = get_settings()

app = FastAPI()
app = FastAPI(title=settings.app_title, version=settings.app_version)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = exc.errors()
    logger.error(str(details[0]['loc']))
    if 'email' in details[0]['loc']:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status_code": 422, 
                "status":"fail",
                "message": details[0]['msg'].split(",")[-1].lstrip(),
                "error_message": details[0]['msg']
            })
        )
    
    if 'phone' in details[0]['loc']:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status_code": 422, 
                "status":"fail",
                "message": "Mobile number is not valid",
                "error_message": details[0]['msg']
            })
        )
    
    if 'password' in details[0]['loc']:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status_code": 422, 
                "status":"fail",
                "message": details[0]['msg'].split(",")[-1].lstrip(),
                "error_message": details[0]['msg']
            })
        )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
                "status_code": 422, 
                "status":"fail",
                "message": details[0]['msg'].split(",")[-1].lstrip(),
                "error_message": details[0]['msg'],
                "detail": exc.errors(),
            }
        )
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
