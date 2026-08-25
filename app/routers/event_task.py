from fastapi import APIRouter, Depends, status, Request
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.schemas.event_task_schema import EventTaskResponse, EventTaskUpdate
from app.models.user import UserModel
from app.services import event_task_service
from app.utils.response import success_response
from app.dependencies.dependency import get_current_user

event_task_router = APIRouter(
    prefix= "/event-tasks",
    tags= ["Event Tasks"]
)

@event_task_router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết một công việc",
    description="Chỉ thành viên thuộc sự kiện chứa công việc này mới có quyền truy cập.",
)
def get_event_task_detail(
    request : Request,
    task_id : int,
    db : Session = Depends(get_db), 
    current_user : UserModel = Depends(get_current_user)
):
    event_detail = event_task_service.get_event_task_detail(db, task_id, current_user)

    response_data = EventTaskResponse.model_validate(event_detail).model_dump()

    return success_response(
        request= request,
        status_code= 200,
        message= "Lấy chi tiết công việc thành công",
        data= response_data
    )

@event_task_router.patch(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Cập nhật công việc sự kiện",
    description="""
    Phân quyền cập nhật:
    * **OWNER của Event**: Sửa được toàn bộ các thông tin.
    * **ASSIGNEE (Người được giao task)**: Chỉ được quyền cập nhật trường `status`.
    * **Thành viên khác**: Bị chặn 403 Forbidden.
    """
)
def update_event_task(
    request : Request,
    task_id : int,
    task_in : EventTaskUpdate,
    db : Session = Depends(get_db),
    current_user : UserModel  = Depends(get_current_user)
):
    update_data = event_task_service.update_event_task(db, task_id, task_in, current_user)

    response_data = EventTaskResponse.model_validate(update_data).model_dump()

    return success_response(
        request= request,
        status_code= 200,
        message= "Cập nhật công việc thành công",
        data= response_data
    )

@event_task_router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa công việc sự kiện",
    description="Chỉ **OWNER của sự kiện** mới có quyền xóa công việc.",
)
def delete_event_task(
    request : Request,
    task_id : int,
    db : Session = Depends(get_db),
    current_user : UserModel = Depends(get_current_user)
):
    delete_data = event_task_service.delete_event_task(db, task_id, current_user)

    return success_response(
        request= request,
        status_code= 200,
        message= "Xóa công việc thành công",
        data= delete_data
    )