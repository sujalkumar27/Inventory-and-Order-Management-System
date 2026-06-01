from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthError, ForbiddenError
from app.core.security import ACCESS_TOKEN_TYPE, decode_token
from app.db.session import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login/oauth")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != ACCESS_TOKEN_TYPE:
        raise AuthError("Could not validate credentials")
    user = db.get(User, payload["sub"])
    if not user or user.is_deleted or not user.is_active:
        raise AuthError("User not found or inactive")
    return user


def require_admin(current: User = Depends(get_current_user)) -> User:
    if current.role != UserRole.ADMIN:
        raise ForbiddenError("Admin privileges required")
    return current
