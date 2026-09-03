from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user_schemas import PublicUser
from ..services.user_service import UserService
from ..services.key_service import KeyService
from ..core.security_deps import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[PublicUser])
def list_users(
    user: User = Depends(get_current_user),
    _: str = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return UserService(db).list_public(user, "admin")


@router.post("/users/{user_id}/disable")
def disable_user(
    user_id: int,
    _: str = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    UserService(db).set_active(user_id, False)
    return {"message": "user disabled"}


@router.post("/users/{user_id}/enable")
def enable_user(
    user_id: int,
    _: str = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    UserService(db).set_active(user_id, True)
    return {"message": "user enabled"}


@router.post("/users/{user_id}/rotate-keys")
def rotate_keys(
    user_id: int,
    _: str = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return KeyService(db).rotate_user_keys(user_id)
