from fastapi import FastAPI
from app.db.database import Base, engine
from app.models import event, event_task, user
from app.routers.health import health_check_router

app = FastAPI(
    title= "Event Management"
)

Base.metadata.create_all(bind = engine)

app.include_router(health_check_router)

@app.get("/")
def test_connect():
    return {
        "message" : "Event Management API is running!"
    }