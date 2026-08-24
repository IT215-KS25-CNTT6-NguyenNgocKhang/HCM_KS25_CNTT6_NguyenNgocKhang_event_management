from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserLogin
from app.models.user import UserModel
from app.core.exceptions import BadRequestException, ForbiddenException
from app.core.security import hash_password, verify_password
from typing import Optional

def create_user(db : Session, user : UserCreate):
    existing = db.query(UserModel).filter(UserModel.email == user.email).first()

    if existing:
        raise BadRequestException(
            message= "Email đã tồn tại!", 
            error= "EMAIL_ALREADY_EXISTS"
            )

    hashed_password = hash_password(user.password)

    new_user = UserModel(
        email = user.email,
        password_hash = hashed_password,
        full_name = user.full_name,
        role = user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login(db : Session, user : UserLogin):
    user_data = db.query(UserModel).filter(UserModel.email == user.email).first()

    if not user_data or not verify_password(user.password, user_data.password_hash):
        raise BadRequestException(
            message= "Email hoặc mật khẩu không chính xác",
            error= "INVALID_CREDENTIALS"
        )

    if not user_data.is_active:
        raise ForbiddenException(
            message="Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên!",
            error="ACCOUNT_INACTIVE"
        )

    return user_data

# Chỉ ADMIN mới sử dụng
def get_all_user(
    db: Session, 
    search_name: Optional[str] = None, 
    search_email: Optional[str] = None, 
    search_status: Optional[bool] = None
):
    query = db.query(UserModel)

    # Nối điều kiện và gán lại vào biến query (không gọi .all() ở đây)
    if search_name:
        query = query.filter(UserModel.full_name.ilike(f"%{search_name.strip()}%"))

    if search_email and "@" in search_email:
        query = query.filter(UserModel.email.ilike(f"%{search_email.strip()}%"))

    if search_status is not None:
        query = query.filter(UserModel.is_active == search_status)

    # Chỉ thực thi truy vấn và lấy toàn bộ danh sách ở bước cuối cùng
    return query.all()