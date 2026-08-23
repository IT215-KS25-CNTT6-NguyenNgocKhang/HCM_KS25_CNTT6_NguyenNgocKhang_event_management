from fastapi import HTTPException, status
from typing import Any

# Tạo lỗi gốc
class ExceptionBase(HTTPException):
    def __init__(self, status_code: int, message: str, error: Any = None):
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.error = error
        
# Lỗi không tìm thấy
class NotFoundException(ExceptionBase):
    def __init__(self, message: str = "Tài nguyên không tồn tại", error: Any = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message, error=error)
        
# Lỗi gửi yêu cầu không hợp lệ
class BadRequestException(ExceptionBase):
    def __init__(self, message: str = "Dữ liệu yêu cầu không hợp lệ", error: Any = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message, error=error)

# Lỗi quyền truy cập
class ForbiddenException(ExceptionBase):
    def __init__(self, message: str = "Bạn không có quyền truy cập", error: Any = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message, error=error)

class UnauthorizedException(ExceptionBase):
    def __init__(self, message: str = "Không thể xác thực thông tin đăng nhập", error: Any = None):
        super().__init__(status_code = status.HTTP_401_UNAUTHORIZED, message= message, error= error)