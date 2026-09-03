from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.record_schemas import RecordCreate, RecordUpdate, RecordView
from ..services.record_service import RecordService
from ..core.security_deps import get_current_user, get_current_role

router = APIRouter(prefix="/records", tags=["records"])


@router.get("", response_model=list[RecordView])
def list_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RecordService(db).list_mine(user)


@router.post("", response_model=RecordView)
def create_record(
    body: RecordCreate,
    user: User = Depends(get_current_user),
    role: str = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    return RecordService(db).create(user, role, body)


@router.get("/{record_id}", response_model=RecordView)
def get_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecordService(db).get(user, record_id)


@router.put("/{record_id}", response_model=RecordView)
def update_record(
    record_id: int,
    body: RecordUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecordService(db).update(user, record_id, body)
