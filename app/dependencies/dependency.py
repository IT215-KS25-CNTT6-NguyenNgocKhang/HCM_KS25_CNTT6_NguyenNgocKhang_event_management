from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
import jwt
from app.core.config import settings
from app.models.user import UserModel
from app.core.exceptions import UnauthorizedException, NotFoundException, ForbiddenException


resuable_oauth2 = HTTPBearer()

async def get_current_user(
    credentials : HTTPAuthorizationCredentials = Depends(resuable_oauth2), 
    db : Session = Depends(get_db)
):
    # lấy chuỗi token
    token = credentials.credentials

    try:
        # Giải token bằng SECRET_KEY
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms= [settings.ALGORITHM])

        email : str = payload.get("sub")

        if email is None:
            raise UnauthorizedException(error= "Token payload missing 'sub' claim")

    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(
            message= "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!",
            error= "TOKEN_EXPIRED"
        ) 

    except jwt.PyJWTError as j:
        raise UnauthorizedException(
            message="Token không hợp lệ hoặc sai định dạng!",
            error= str(j)
        )

    # Truy vấn thông tin người dùng 
    user = db.query(UserModel).filter(UserModel.email == email).first()

    if user is None:
        raise NotFoundException(
            error= "NOT_FOUND"
        )

    # Kiểm tra tài khoản có bị khóa hay không
    if not user.is_active:
        raise ForbiddenException(
            message="Tài khoản này đã bị vô hiệu hóa hoặc tạm khóa!",
            error= "ACCESS_DENIED"
        )

    return user

class RoleChecker():
    # Lưu lại danh sách role được phép khi khởi tạo
    def __init__(self, allowed_roles : list[str]):
        self.allowed_roles = allowed_roles

    # Lấy tên role từ relationship object
    def __call__(self, current_user : UserModel = Depends(get_current_user)):
        user_role_name = current_user.role if current_user.role else None

        # Kiểm tra role của user có nằm trong danh sách được phép không
        if user_role_name not in self.allowed_roles:
            raise ForbiddenException(
                message= f"Quyền truy cập bị từ chối! Yêu cầu một trong các quyền: {self.allowed_roles}",
                error= "ACCESS_DENIED"
            )
        
        return current_user
    
    