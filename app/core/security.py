import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

# Hàm băm mật khẩu
def hash_password(password : str, cost_factor : int = 12):
    # chuyển str -> bytes
    password_bytes = password.encode('utf-8')
    # tạo salt
    salt = bcrypt.gensalt(rounds= cost_factor)
    # tiến hành băm
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password : str, hashed_password : str):
    # chuyen sang dang Byte
    plain_bytes = plain_password.encode('utf-8')
    hashed_byted = hashed_password.encode('utf-8')
    # kiem tra va tra ve Boolean
    return bcrypt.checkpw(plain_bytes, hashed_byted)

def create_access_token(data : dict):
    # sao chép dữ liệu User
    to_encode = data.copy()

    # tính toán thời gian hết hạn
    expire = datetime.now(timezone.utc) + timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp" : expire
    })

    # Tạo chuỗi JWT
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm= settings.ALGORITHM)

    return encode_jwt