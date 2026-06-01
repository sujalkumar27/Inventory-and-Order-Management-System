from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.session import SessionLocal
from app.models.user import UserRole
from app.schemas.auth import UserRegister
from app.services import user_service


def _bootstrap_admin() -> None:
    if not (settings.FIRST_ADMIN_EMAIL and settings.FIRST_ADMIN_PASSWORD):
        return
    db = SessionLocal()
    try:
        if not user_service.get_by_email(db, settings.FIRST_ADMIN_EMAIL):
            user_service.register_user(
                db,
                UserRegister(
                    full_name=settings.FIRST_ADMIN_NAME,
                    email=settings.FIRST_ADMIN_EMAIL,
                    password=settings.FIRST_ADMIN_PASSWORD,
                ),
                role=UserRole.ADMIN,
            )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        _bootstrap_admin()
    except Exception:  # pragma: no cover - bootstrap is best effort
        pass
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["health"])
def health():
    return {"success": True, "message": "ok"}
