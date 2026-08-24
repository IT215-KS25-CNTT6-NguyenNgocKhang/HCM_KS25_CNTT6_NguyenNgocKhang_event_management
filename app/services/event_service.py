from sqlalchemy.orm import Session
from app.models.event import EventModel, EventStaffModel
from app.models.user import UserModel
from app.schemas.event_schema import EventCreate, EventUpdate
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from typing import Optional



# hàm kiểm tra quyền nội bộ trong event
def get_user_event_role(
    db: Session, event_id: int, user_id: int
):
    staff = db.query(EventStaffModel).filter(
            EventStaffModel.event_id == event_id,
            EventStaffModel.user_id == user_id,
        ).first()
    
    return staff.role if staff else None

# Thêm sự kiện
def create_event(db : Session, event_in : EventCreate, user_in : UserModel):
    existing = db.query(EventModel).filter(EventModel.name == event_in.name).first()
    if existing:
        raise BadRequestException(
            message="Tên sự kiện đã tồn tại!", 
            error="EVENT_NAME_ALREADY_EXISTS"
        )

    new_event = EventModel(
        name= event_in.name,
        description= event_in.description,
        owner_id= user_in.id
    )

    db.add(new_event)
    db.flush()

    staff = EventStaffModel(
        event_id= new_event.id,
        user_id= user_in.id,
        role= "OWNER"
    )

    db.add(staff)
    db.commit()
    db.refresh(new_event)

    return new_event

# lấy tất cả sự kiện
def get_user_events(db : Session, user_id : int, search : Optional[str] = None):
    query = db.query(EventModel).join(EventStaffModel, EventModel.id == EventStaffModel.event_id).filter(EventStaffModel.user_id == user_id)

    if search:
        query = query.filter(EventModel.name.ilike(f"%{search.strip()}%"))

    return query.all()

# lấy 1 sự kiện 
def get_event_detail(db : Session, event_id : int, current_user : UserModel):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()

    if not event:
        raise NotFoundException(
            message="Sự kiện không tồn tại!", 
            error="EVENT_NOT_FOUND"
        )

    role = get_user_event_role(db, event_id, current_user.id)
    if not role:
        raise ForbiddenException(
            message="Bạn không phải thành viên của sự kiện này!",
            error="NOT_EVENT_MEMBER",
        )

    return event

# cập nhật sự kiện (chỉ OWNER)
def update_event(
    db: Session,
    event_id: int,
    event_update: EventUpdate,
    current_user: UserModel,
):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise NotFoundException(
            message="Sự kiện không tồn tại!", 
            error="EVENT_NOT_FOUND"
        )

    role = get_user_event_role(db, event_id, current_user.id)
    if role != "OWNER":
        raise ForbiddenException(
            message="Chỉ OWNER mới có quyền chỉnh sửa sự kiện!",
            error="ONLY_OWNER_ALLOWED",
        )

    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


# Xóa sự kiện (chỉ OWNER)
def delete_event(db: Session, event_id: int, current_user: UserModel):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise NotFoundException(
            message="Sự kiện không tồn tại!", 
            error="EVENT_NOT_FOUND"
        )

    role = get_user_event_role(db, event_id, current_user.id)
    if role != "OWNER":
        raise ForbiddenException(
            message="Chỉ OWNER mới có quyền xóa sự kiện!",
            error="ONLY_OWNER_ALLOWED",
        )

    # Xóa thành viên liên quan và xóa sự kiện
    db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id).delete()

    db.delete(event)
    db.commit()

# Thêm thành viên (chỉ OWNER thêm, không thêm trùng)
def add_member(
    db: Session,
    event_id: int,
    target_user_id: int,
    member_role: str,
    current_user: UserModel,
):
    # Kiểm tra event tồn tại
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise NotFoundException(
            message="Sự kiện không tồn tại!", error="EVENT_NOT_FOUND"
        )

    # Quyền người thực hiện
    role = get_user_event_role(db, event_id, current_user.id)
    if role != "OWNER":
        raise ForbiddenException(
            message="Chỉ OWNER mới có quyền thêm thành viên!",
            error="ONLY_OWNER_ALLOWED",
        )

    # Kiểm tra user cần thêm có tồn tại không
    target_user = (
        db.query(UserModel).filter(UserModel.id == target_user_id).first()
    )
    if not target_user:
        raise NotFoundException(
            message="Người dùng không tồn tại!", error="USER_NOT_FOUND"
        )

    # Kiểm tra đã tham gia chưa
    existing_staff = (
        db.query(EventStaffModel)
        .filter(
            EventStaffModel.event_id == event_id,
            EventStaffModel.user_id == target_user_id,
        )
        .first()
    )
    if existing_staff:
        raise BadRequestException(
            message="Người dùng này đã là thành viên của sự kiện!",
            error="MEMBER_EXISTS",
        )

    new_staff = EventStaffModel(
        event_id=event_id, user_id=target_user_id, role=member_role
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff


# Lấy danh sách thành viên trong sự kiện (chỉ Member xem)
def get_event_members(
    db: Session, event_id: int, current_user: UserModel
) -> list:
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise NotFoundException(
            message="Sự kiện không tồn tại!", error="EVENT_NOT_FOUND"
        )

    role = get_user_event_role(db, event_id, current_user.id)
    if not role:
        raise ForbiddenException(
            message="Bạn không phải thành viên của sự kiện!",
            error="NOT_EVENT_MEMBER",
        )

    # Query join lấy thông tin UserModel và role
    members = db.query(
            UserModel.id.label("user_id"),
            UserModel.email,
            UserModel.full_name,
            EventStaffModel.role,
            EventStaffModel.joined_at,
        ).join(EventStaffModel, UserModel.id == EventStaffModel.user_id).filter(EventStaffModel.event_id == event_id).all()

    return members


# Xóa thành viên (chỉ OWNER xóa, không được xóa OWNER cuối cùng)
def remove_member(
    db: Session, event_id: int, target_user_id: int, current_user: UserModel
):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise NotFoundException(
            message="Sự kiện không tồn tại!", error="EVENT_NOT_FOUND"
        )

    # Người thực hiện phải là OWNER
    role = get_user_event_role(db, event_id, current_user.id)
    if role != "OWNER":
        raise ForbiddenException(
            message="Chỉ OWNER mới có quyền xóa thành viên!",
            error="ONLY_OWNER_ALLOWED",
        )

    # Kiểm tra target member có trong event không
    target_staff = (
        db.query(EventStaffModel)
        .filter(
            EventStaffModel.event_id == event_id,
            EventStaffModel.user_id == target_user_id,
        )
        .first()
    )
    if not target_staff:
        raise NotFoundException(
            message="Thành viên không thuộc sự kiện này!",
            error="MEMBER_NOT_FOUND",
        )

    # Ràng buộc: Không được xóa OWNER cuối cùng
    if target_staff.role == "OWNER":
        owner_count = db.query(EventStaffModel).filter(
                EventStaffModel.event_id == event_id,
                EventStaffModel.role == "OWNER",
            ).count()
        
        if owner_count <= 1:
            raise BadRequestException(
                message="Không thể xóa OWNER cuối cùng của sự kiện!",
                error="CANNOT_REMOVE_LAST_OWNER",
            )

    db.delete(target_staff)
    db.commit()