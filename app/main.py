from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.db.database import Base, engine
from app.models import event, event_task, user
from app.routers.health import health_check_router
from app.routers.auth import auth_router
from app.routers.user import user_router
from app.routers.event import event_router
from app.core.exceptions import ExceptionBase
from app.utils.response import error_response

app = FastAPI(
    title= "Event Management"
)

Base.metadata.create_all(bind = engine)

app.include_router(health_check_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(event_router)

@app.exception_handler(ExceptionBase)
async def custom_exception_handler(request : Request, exc : ExceptionBase):
    return error_response(
        request= request,
        status_code= exc.status_code,
        message= exc.message,
        error= exc.error
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        request= request,
        status_code= status.HTTP_422_UNPROCESSABLE_CONTENT,
        message= "Dữ liệu đầu vào không hợp lệ",
        error= exc.errors()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Đã xảy ra lỗi hệ thống bên trong server",
        error=str(exc),
    )

@app.get("/")
def test_connect():
    return {
        "message" : "Event Management API is running!"
    }