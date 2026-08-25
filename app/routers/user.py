from fastapi import APIRouter, Depends, status, Request
from app.models.user import UserModel
from app.dependencies.dependency import get_current_user, RoleChecker
from app.services import user_service
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import user_schema
from app.utils.response import success_response
from typing import Optional

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin cá nhân",
    description="Xem thông tin chi tiết của tài khoản đang đăng nhập thông qua Bearer Token.",
)
def get_my_profile(request : Request, current_user: UserModel = Depends(get_current_user)):
    user_info = user_schema.UserResponse(
        id= current_user.id,
        email= current_user.email,
        full_name= current_user.full_name,
        role= current_user.role,
        is_active= current_user.is_active,
        created_at= current_user.created_at,
    )

    return success_response(
        request= request,
        status_code= 200,
        message= "Lấy thông tin thành công",
        data= user_info
    )


@user_router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách người dùng (Chỉ ADMIN)",
    description="Dành riêng cho quản trị viên hệ thống. Hỗ trợ lọc theo họ tên, email và trạng thái hoạt động.",
)
def get_all_user(
    request : Request, 
    search_name: Optional[str] = None,
    search_email: Optional[str] = None,
    search_status: Optional[bool] = None,
    current_user: UserModel = Depends(RoleChecker(["ADMIN"])),
    db: Session = Depends(get_db),
):
    data = user_service.get_all_user(db, search_name, search_email, search_status)

    response_data = [user_schema.UserResponse.model_validate(u) for u in data]

    return success_response(
        request= request,
        status_code= 200,
        message= "Xác thực thành công! Chào mừng Admin!",
        data= response_data
    )