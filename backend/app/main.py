from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import get_engine, get_session_factory, Base
from .core.exceptions import PulseCryptError
from .routers import auth_router, user_router, record_router, admin_router, key_router
from .models import user, patient_profile, medical_record, key_record, session_token  # noqa: F401
from .services.key_service import get_master
from .services.auth_service import AuthService
from .middleware.session_middleware import SessionAuthMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    get_master()
    db = get_session_factory()()
    try:
        AuthService(db).seed_admin()
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(SessionAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PulseCryptError)
async def pulsecrypt_error_handler(_: Request, exc: PulseCryptError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(record_router.router)
app.include_router(admin_router.router)
app.include_router(key_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
