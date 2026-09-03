"""
Request-level check that the Authorization bearer token decrypts and
passes HMAC verification before protected routes run.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..core.exceptions import PulseCryptError
from ..database import get_session_factory
from ..services.session_service import SessionService

_PUBLIC = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/register",
    "/auth/login",
    "/auth/verify-2fa",
}


def _is_public(path: str) -> bool:
    if path in _PUBLIC:
        return True
    if path.startswith("/docs") or path.startswith("/redoc"):
        return True
    return False


class SessionAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or _is_public(request.url.path):
            return await call_next(request)

        header = request.headers.get("authorization")
        db = get_session_factory()()
        try:
            if not header:
                raise PulseCryptError("missing Authorization header", 401)
            parts = header.split(" ", 1)
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise PulseCryptError("expected Bearer token", 401)
            payload = SessionService(db).parse(parts[1].strip())
            request.state.session = payload
        except PulseCryptError as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
        finally:
            db.close()

        return await call_next(request)
