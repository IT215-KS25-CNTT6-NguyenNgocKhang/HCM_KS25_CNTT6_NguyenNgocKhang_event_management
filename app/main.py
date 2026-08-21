from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.db.database import Base, engine
from app.models import event, event_task, user
from app.routers.health import health_check_router
from app.core.exceptions import ExceptionBase

app = FastAPI(
    title= "Event Management"
)

Base.metadata.create_all(bind = engine)

app.include_router(health_check_router)

@app.exception_handler(ExceptionBase)
async def custom_exception_handler(request : Request, exc : ExceptionBase):
    return JSONResponse(
        status_code= exc.status_code,
        content= {
            "status_code": exc.status_code,
            "message": exc.message,
            "error": exc.error
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": 422,
            "message": "Dữ liệu đầu vào không hợp lệ",
            "error": exc.errors(),
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "message": "Đã xảy ra lỗi hệ thống",
            "error": str(exc),
        },
    )

@app.get("/")
def test_connect():
    return {
        "message" : "Event Management API is running!"
    }