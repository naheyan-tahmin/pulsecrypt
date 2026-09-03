from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user_schemas import ProfileView, ProfileUpdate
from ..services.user_service import UserService
from ..core.security_deps import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileView)
def read_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return UserService(db).view_profile(user)


@router.put("", response_model=ProfileView)
def update_profile(
    body: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).update_profile(user, body)
