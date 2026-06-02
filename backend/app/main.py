import logging
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ioms")

INSECURE_SECRETS = {"change-me-in-production", "change-me", "secret", ""}


def _verify_production_config() -> None:
    """Fail fast on insecure configuration when running in production."""
    if not settings.is_production:
        return
    if settings.SECRET_KEY in INSECURE_SECRETS:
        raise RuntimeError(
            "SECRET_KEY is missing or set to an insecure default. "
            "Set a strong, unique SECRET_KEY before deploying to production."
        )


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
    _verify_production_config()
    try:
        _bootstrap_admin()
    except Exception:  # pragma: no cover - bootstrap is best effort
        logger.exception("Admin bootstrap failed")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

_origins = [str(o) for o in settings.BACKEND_CORS_ORIGINS]
_allow_all = "*" in _origins
if _origins:
    app.add_middleware(
        CORSMiddleware,
        # "*" allows any origin. Browsers forbid credentials with "*", but auth
        # here uses bearer tokens (not cookies), so credentials aren't required.
        allow_origins=["*"] if _allow_all else _origins,
        allow_credentials=not _allow_all,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["health"])
def health():
    return {"success": True, "message": "ok"}
