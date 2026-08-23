from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Any
from datetime import datetime, timezone

def success_response(
    request: Request,
    status_code: int,
    message: str,
    data: Any = None
):
    return {
        "status_code": status_code,
        "message": message,
        "data": data,
        "error": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": request.url.path
    }

def error_response(
    request: Request,
    status_code: int,
    message: str,
    error: Any = None,
):
    return JSONResponse(
        status_code= status_code,
        content= {
            "status_code": status_code,
            "message": message,
            "data": None,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path
        }
    )
