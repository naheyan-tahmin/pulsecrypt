from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth_schemas import RegisterRequest, LoginRequest, TotpVerifyRequest, TokenResponse
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(body)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(body.username, body.password)


@router.post("/verify-2fa", response_model=TokenResponse)
def verify_2fa(body: TotpVerifyRequest, db: Session = Depends(get_db)):
    return AuthService(db).verify_2fa(body.pre2fa_token, body.code)
