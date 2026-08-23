from fastapi import APIRouter, Depends, status
from app.models.user import UserModel
from app.dependencies.dependency import get_current_user, RoleChecker
from app.services import user_service
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import user_schema
from typing import List
from app.utils.response import success_response
from typing import Optional

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("/me", status_code=status.HTTP_200_OK)
def get_my_profile(current_user: UserModel = Depends(get_current_user)):
    user_info = user_schema.UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )

    return success_response(
        data=user_info, message="Xác thực thành công", status_code=200
    )


@user_router.get("", status_code=status.HTTP_200_OK)
def get_all_user(
    search_name: Optional[str] = None,
    search_email: Optional[str] = None,
    search_status: Optional[bool] = None,
    current_user: UserModel = Depends(RoleChecker(["ADMIN"])),
    db: Session = Depends(get_db),
):
    data = user_service.get_all_user(db, search_name, search_email, search_status)

    response_data = [user_schema.UserResponse.model_validate(u) for u in data]

    return success_response(
        data=response_data,
        message="Xác thực thành công! Chào mừng Admin!",
        status_code=200,
    )
