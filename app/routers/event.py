from fastapi import APIRouter, Depends, status, Request, Query
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.schemas.event_schema import EventCreate, EventResponse, EventUpdate
from app.schemas.event_staff_schema import EventStaffCreate, EventStaffResponse
from app.schemas.event_task_schema import EventTaskCreate, EventTaskUpdate, EventTaskResponse
from app.models.user import UserModel
from app.services import event_service
from app.services import event_task_service
from app.utils.response import success_response
from app.dependencies.dependency import get_current_user
from typing import Optional, Literal


event_router = APIRouter(prefix="/events", tags=["Events"])

# Tạo sự kiện
@event_router.post(
    "", 
    status_code=status.HTTP_201_CREATED,
    summary="Tạo sự kiện mới",
    description="Bất kỳ người dùng đã đăng nhập nào cũng có thể tạo sự kiện. Người tạo sẽ tự động được gán quyền `OWNER`.",
)
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
@event_router.get(
    "", 
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách sự kiện",
    description="Trả về danh sách các sự kiện mà người dùng hiện tại đang tham gia (`OWNER` hoặc `MEMBER`). Hỗ trợ tìm kiếm theo tên."
)
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
@event_router.get(
    "/{event_id}", 
    status_code= status.HTTP_200_OK,
    summary="Xem chi tiết sự kiện",
    description="Xem thông tin chi tiết của một sự kiện. Chỉ thành viên thuộc sự kiện mới có quyền xem (Chặn 403 nếu là người ngoài)."
) 
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
@event_router.patch(
    "/{event_id}", 
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin sự kiện",
    description="Cập nhật tên/mô tả sự kiện. **Chỉ OWNER của sự kiện** mới có quyền thao tác."
)
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
@event_router.delete(
    "/{event_id}", 
    status_code=status.HTTP_200_OK,
    summary="Xóa sự kiện",
    description="Xóa hoàn toàn một sự kiện. **Chỉ OWNER của sự kiện** mới có quyền xóa."
)
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
    "/{event_id}/members", 
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên vào sự kiện",
    description="Chỉ `OWNER` mới có quyền thêm thành viên mới. Báo lỗi 400 nếu thành viên đã tồn tại."
)
def add_member(
    request: Request,
    event_id: int,
    member_in: EventStaffCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = event_service.add_member(
        db=db,
        event_id=event_id,
        target_user_id=member_in.user_id,
        current_user=current_user,
    )

    response_data = EventStaffResponse.model_validate(data).model_dump()

    return success_response(
        request=request,
        status_code=201,
        message="Thêm thành viên vào sự kiện thành công!",
        data=response_data,
    )


# Danh sách thành viên trong sự kiện (Chỉ Member xem)
@event_router.get(
    "/{event_id}/members", 
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách thành viên",
    description="Liệt kê danh sách toàn bộ ban tổ chức (Owner & Member) của sự kiện."
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
    "/{event_id}/members/{user_id}", 
    status_code=status.HTTP_200_OK,
    summary="Xóa thành viên khỏi sự kiện",
    description="Chỉ `OWNER` mới có quyền xóa. Ngăn chặn việc xóa mất `OWNER` duy nhất còn lại của sự kiện."
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


@event_router.post(
    "/{event_id}/event-tasks", 
    status_code= status.HTTP_201_CREATED,
    summary="Tạo công việc mới trong sự kiện",
    description="Thành viên hoặc Owner trong sự kiện đều có thể tạo công việc. Assignee bắt buộc phải thuộc ban tổ chức sự kiện."
)
def create_event_task(request : Request, event_id : int, event_task_in : EventTaskCreate,db : Session = Depends(get_db), current_user : UserModel = Depends(get_current_user)):
    data = event_task_service.create_event_task(db, event_task_in, event_id, current_user)

    response_data = EventTaskResponse.model_validate(data)

    return success_response(
        request= request,
        status_code= 201,
        message= "Thêm công việc sự kiện thành công!",
        data= response_data.model_dump()
    )

@event_router.get(
    "/{event_id}/event-tasks", 
    status_code= status.HTTP_200_OK,
    summary="Lấy danh sách công việc của sự kiện",
    description="Tìm kiếm, lọc theo status, priority, assignee và hỗ trợ phân trang (Pagination), sắp xếp (Sort)."
)
def get_event_tasks(
    request : Request, 
    event_id : int,
    title : Optional[str] = None,
    status : Optional[str] = None,
    priority : Optional[str] = None,
    assignee_id: Optional[int] = None,
    sort_by: Literal["created_at", "due_date"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db : Session = Depends(get_db), 
    current_user : UserModel = Depends(get_current_user)
):
    event_tasks = event_task_service.get_event_tasks(
        db,
        event_id,
        current_user,
        title,
        status,
        priority,
        assignee_id,
        sort_by,
        order,
        page,
        page_size,
    )

    response_data = {
        "items": [EventTaskResponse.model_validate(t).model_dump() for t in event_tasks["items"]],
        "total": event_tasks["total"],
        "page": event_tasks["page"],
        "page_size": event_tasks["page_size"],
        "total_pages": event_tasks["total_pages"],
    }

    return success_response(
        request= request,
        status_code= 200,
        message= "Lấy danh sách công việc sự kiện thành công",
        data= response_data
    )