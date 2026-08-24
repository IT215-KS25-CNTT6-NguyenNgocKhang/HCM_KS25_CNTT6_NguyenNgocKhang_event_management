from fastapi import APIRouter, Depends, status, Request
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.schemas.event_schema import EventCreate, EventResponse, EventUpdate
from app.schemas.event_staff_schema import EventStaffCreate, EventStaffResponse
from app.models.user import UserModel
from app.services import event_service
from app.utils.response import success_response
from app.dependencies.dependency import get_current_user
from typing import Optional

event_router = APIRouter(prefix="/events", tags=["Events"])

# Tạo sự kiện
@event_router.post("", status_code=status.HTTP_201_CREATED)
def create_event(
    request: Request,
    event_in: EventCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_event = event_service.create_event(db, event_in, current_user)

    event_data = EventResponse.model_validate(new_event)

    return success_response(
        request= request,
        status_code= 201,
        message= "Thêm sự kiện thành công!",
        data= event_data.model_dump(),
    )

# lấy tất cả sự kiện
@event_router.get("", status_code=status.HTTP_200_OK)
def get_user_event(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    events = event_service.get_user_events(db, user_id=current_user.id, search=name)

    data = [EventResponse.model_validate(e).model_dump() for e in events]

    return success_response(
        request= request,
        status_code= 200,
        message= "Lấy danh sách sự kiện thành công!",
        data= data,
    )

# lấy sự kiện theo user hiện tại
@event_router.get("/{event_id}", status_code= status.HTTP_200_OK) 
def get_event_detail(
    request : Request,
    event_id : int,
    db : Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    event_data = event_service.get_event_detail(db, event_id, current_user)

    response_event = EventResponse.model_validate(event_data)

    return success_response(
        request= request,
        status_code= 200,
        message= "Lấy chi tiết sự kiện thành công!",
        data= response_event.model_dump(),
    )

# Cập nhật sự kiện (Chỉ OWNER)
@event_router.patch("/{event_id}", status_code=status.HTTP_200_OK)
def update_event(
    request: Request,
    event_id: int,
    event_in: EventUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated = event_service.update_event(db, event_id, event_in, current_user)

    data = EventResponse.model_validate(updated)

    return success_response(
        request=request,
        status_code=200,
        message="Cập nhật sự kiện thành công!",
        data=data.model_dump(),
    )


# Xóa sự kiện (Chỉ OWNER)
@event_router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(
    request: Request,
    event_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event_service.delete_event(db, event_id, current_user)
    
    return success_response(
        request=request,
        status_code=200,
        message="Xóa sự kiện thành công!",
        data=None,
    )


# Thêm thành viên vào sự kiện (Chỉ OWNER)
@event_router.post(
    "/{event_id}/members", status_code=status.HTTP_201_CREATED
)
def add_member(
    request: Request,
    event_id: int,
    member_in: EventStaffCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event_service.add_member(
        db=db,
        event_id=event_id,
        target_user_id=member_in.user_id,
        member_role=member_in.role,
        current_user=current_user,
    )

    return success_response(
        request=request,
        status_code=201,
        message="Thêm thành viên vào sự kiện thành công!",
        data=None,
    )


# Danh sách thành viên trong sự kiện (Chỉ Member xem)
@event_router.get(
    "/{event_id}/members", status_code=status.HTTP_200_OK
)
def get_event_members(
    request: Request,
    event_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    members = event_service.get_event_members(db, event_id, current_user)

    data = [EventStaffResponse.model_validate(m).model_dump() for m in members]

    return success_response(
        request=request,
        status_code=200,
        message="Lấy danh sách thành viên thành công!",
        data=data,
    )


# Xóa thành viên khỏi sự kiện (Chỉ OWNER, không xóa OWNER cuối cùng)
@event_router.delete(
    "/{event_id}/members/{user_id}", status_code=status.HTTP_200_OK
)
def remove_member(
    request: Request,
    event_id: int,
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event_service.remove_member(
        db=db,
        event_id=event_id,
        target_user_id=user_id,
        current_user=current_user,
    )

    return success_response(
        request=request,
        status_code=200,
        message="Xóa thành viên khỏi sự kiện thành công!",
        data=None,
    )