from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

health_check_router = APIRouter(
    prefix="/health", 
    tags=["Health Check"]
)

@health_check_router.get("")
def health_check(db: Session = Depends(get_db)):
    try:
        # Kiểm tra kết nối DB
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "database": db_status
    }