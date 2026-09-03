from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.record_schemas import DhStartRequest, DhAcceptRequest, DhView, ShareRequest, RecordView
from ..schemas.user_schemas import PublicUser
from ..services.record_service import RecordService
from ..services.user_service import UserService
from ..core.security_deps import get_current_user, get_current_role

router = APIRouter(prefix="/keys", tags=["keys"])


@router.get("/directory", response_model=list[PublicUser])
def directory(
    user: User = Depends(get_current_user),
    role: str = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    return UserService(db).list_public(user, role)


@router.post("/dh/start", response_model=DhView)
def dh_start(
    body: DhStartRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecordService(db).start_dh(user, body.peer_user_id)


@router.post("/dh/accept", response_model=DhView)
def dh_accept(
    body: DhAcceptRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecordService(db).accept_dh(user, body.exchange_id)


@router.get("/dh", response_model=list[DhView])
def dh_list(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RecordService(db).list_dh(user)


@router.post("/share", response_model=RecordView)
def share_record(
    body: ShareRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecordService(db).share(user, body.record_id, body.exchange_id)
