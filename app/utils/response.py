from typing import Any

def success_response(data : Any = None, message: str = "Thành công", status_code: int = 200):
    return {
        "status_code": status_code,
        "message": message,
        "data": data,
        "error": None
    }