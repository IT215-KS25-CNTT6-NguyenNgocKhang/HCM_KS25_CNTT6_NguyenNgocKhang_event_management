from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate, UserLogin
from app.db.database import get_db
from app.services import user_service
from app.core.security import create_access_token

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK
)
def login(user : UserLogin, db : Session = Depends(get_db)):
    user_data = user_service.login(db, user)

    role_name = user_data.role if user_data.role else "USER"

    access_token = create_access_token(
        data={
            "sub": user_data.email, 
            "id": user_data.id, 
            "role": role_name
        })

    return {
        "message": "Đăng nhập thành công",
        "access_token": access_token,
        "token_type": "bearer",
        "data": {
            "id": user_data.id,
            "email": user_data.email,
            "role": role_name,
            "is_active": user_data.is_active,
            "created_at": user_data.created_at
        }
    }