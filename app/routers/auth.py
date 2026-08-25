from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.db.database import get_db
from app.services import user_service
from app.core.security import create_access_token
from app.utils.response import success_response

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/register", 
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Tạo mới một tài khoản người dùng với email và mật khẩu. Trả về mã lỗi 400 nếu email đã tồn tại.",
)
def register(request : Request, user: UserCreate, db: Session = Depends(get_db)):
    new_user = user_service.create_user(db, user)
    user_data = UserResponse.model_validate(new_user)

    return success_response(
        request=request,
        status_code=status.HTTP_201_CREATED,
        message="Đăng ký tài khoản thành công!",
        data=user_data.model_dump(),
    )


@auth_router.post(
    "/login", 
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập hệ thống",
    description="Xác thực thông tin email/mật khẩu và cấp Access Token dạng JWT."
)
def login(request : Request, user : UserLogin, db : Session = Depends(get_db)):
    user_data = user_service.login(db, user)

    role_name = user_data.role if user_data.role else "USER"

    access_token = create_access_token(
        data={
            "sub": user_data.email,
            "id": user_data.id,
            "role": role_name,
        }
    )

    login_result = {
        "access_token": access_token,
        "token_type": "bearer",
    }

    return success_response(
        request=request,
        status_code=status.HTTP_200_OK,
        message="Đăng nhập thành công!",
        data=login_result,
    )