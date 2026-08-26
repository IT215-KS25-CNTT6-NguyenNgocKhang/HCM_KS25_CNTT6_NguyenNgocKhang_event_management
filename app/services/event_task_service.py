import math
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.models.event import EventModel
from app.models.event_task import EventTaskModel
from app.models.user import UserModel
from app.schemas.event_task_schema import EventTaskCreate, EventTaskUpdate
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from typing import Optional
from app.services.event_service import get_user_event_role

# Thêm task 
def create_event_task(db : Session, event_task_in : EventTaskCreate, event_id : int, current_user : UserModel):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise NotFoundException(
            message="Sự kiện không tồn tại!", 
            error="EVENT_NOT_FOUND"
        )

    role = get_user_event_role(db, event_id, current_user.id)
    if not role:
        raise ForbiddenException(
            message="Bạn không phải thành viên của sự kiện!",
            error="NOT_EVENT_MEMBER",
        )

    # Nếu assignee_id = 0 -> đổi lại thành None
    assignee_id = event_task_in.assignee_id if event_task_in.assignee_id and event_task_in.assignee_id > 0 else None

    if assignee_id is not None:
        assignee_role = get_user_event_role(db, event_id, assignee_id)
        if not assignee_role:
            raise BadRequestException(
                message="Người được giao việc không thuộc sự kiện này!",
                error="ASSIGNEE_NOT_IN_EVENT",
            )

    new_task = EventTaskModel(
            event_id= event_id,
            title= event_task_in.title,
            description= event_task_in.description,
            assignee_id= assignee_id,
            status= "TODO",
            priority= event_task_in.priority,
            due_date= event_task_in.due_date,
        )

    db.add(new_task)
    db.commit()    
    db.refresh(new_task)
    return new_task


# Lấy task
def get_event_tasks(
    db : Session, 
    event_id : int, 
    current_user: UserModel,
    title : Optional[str] = None,
    status : Optional[str] = None,
    priority : Optional[str] = None,
    assignee_id: Optional[int] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    page: int = 1,
    page_size: int = 10,
):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()

    if not event:
        raise NotFoundException(
            message= "Sự kiện không tồn tại",
            error= "EVENT_NOT_FOUND"
        )

    role = get_user_event_role(db, event_id, current_user.id)
    if not role:
        raise ForbiddenException(
            message="Bạn không phải thành viên của sự kiện!",
            error="NOT_EVENT_MEMBER",
        )

    query = db.query(EventTaskModel).filter(
        EventTaskModel.event_id == event_id
    )

    if title:
        query = query.filter(EventTaskModel.title.ilike(f"%{title.strip()}%"))
    if status:
        query = query.filter(EventTaskModel.status == status)
    if priority:
        query = query.filter(EventTaskModel.priority == priority)
    if assignee_id:
        query = query.filter(EventTaskModel.assignee_id == assignee_id)


    sort_column = getattr(EventTaskModel, sort_by, EventTaskModel.created_at)

    if order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Phân trang (Pagination)
    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

def get_event_task_detail(
    db : Session, 
    task_id : int,
    current_user : UserModel
):
    task = db.query(EventTaskModel).filter(EventTaskModel.id == task_id).first()

    if not task:
        raise NotFoundException(
            message="Công việc không tồn tại!", 
            error="TASK_NOT_FOUND"
        )

    role = get_user_event_role(db, task.event_id, current_user.id)
    if not role:
        raise ForbiddenException(
            message="Bạn không có quyền truy cập công việc của sự kiện này!",
            error="NOT_EVENT_MEMBER",
        )

    return task

def update_event_task(
    db : Session,
    task_id : int,
    task_in : EventTaskUpdate,
    current_user : UserModel      
):
    task = db.query(EventTaskModel).filter(EventTaskModel.id == task_id).first()

    if not task:
        raise NotFoundException(
            message="Công việc không tồn tại!", 
            error="TASK_NOT_FOUND"
        )

    event_role = get_user_event_role(db, task.event_id, current_user.id)
    if not event_role:
        raise ForbiddenException(
            message="Bạn không thuộc sự kiện này!", 
            error="NOT_EVENT_MEMBER"
        )

    # Permission
    if not (event_role == "OWNER" or task.assignee_id == current_user.id):
        raise ForbiddenException(
            message="Bạn không có quyền cập nhật công việc này!",
            error="TASK_UPDATE_FORBIDDEN",
        )

    update_data = task_in.model_dump(exclude_unset=True)

    # Nếu chỉ là ASSIGNEE (không phải OWNER), chỉ cho phép sửa status
    if not event_role == "OWNER" and task.assignee_id == current_user.id:

        allowed_fields = {"status"}
        if any(key not in allowed_fields for key in update_data.keys()): 
            raise ForbiddenException(
                message="Người được giao việc chỉ có quyền cập nhật trạng thái (status)!",
                error="ASSIGNEE_STATUS_ONLY",
            )

    # Nếu cập nhật người phụ trách (OWNER đổi assignee_id)
    if "assignee_id" in update_data and update_data.get("assignee_id") is not None:

        assignee_role = get_user_event_role(db, task.event_id, update_data.get("assignee_id"))

        if not assignee_role:
            raise BadRequestException(
                message="Người được giao việc không thuộc sự kiện này!",
                error="ASSIGNEE_NOT_IN_EVENT",
            )

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task

def delete_event_task(
    db : Session,
    task_id : int,
    current_user : UserModel
):
    task = db.query(EventTaskModel).filter(EventTaskModel.id == task_id).first()

    if not task:
        raise NotFoundException(
            message="Công việc không tồn tại!", 
            error="TASK_NOT_FOUND"
        )
    

    event_role = get_user_event_role(db, task.event_id, current_user.id)
    if event_role != "OWNER":
        raise ForbiddenException(
            message="Chỉ OWNER sự kiện mới có quyền xóa công việc!",
            error="ONLY_OWNER_ALLOWED",
        )

    db.delete(task)
    db.commit()
    return True