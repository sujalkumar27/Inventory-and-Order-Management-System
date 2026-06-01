from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AuthError, ConflictError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.auth import TokenPair, UserRegister


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(
        select(User).where(User.email == email, User.is_deleted.is_(False))
    )


def register_user(db: Session, data: UserRegister, role: UserRole = UserRole.USER) -> User:
    if get_by_email(db, data.email):
        raise ConflictError("Email already registered")
    user = User(
        full_name=data.full_name,
        email=str(data.email),
        hashed_password=hash_password(data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid email or password")
    if not user.is_active:
        raise AuthError("User account is inactive")
    return user


def issue_tokens(user: User) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id)),
    )


def refresh_tokens(db: Session, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthError("Invalid refresh token")
    user = db.get(User, payload["sub"])
    if not user or user.is_deleted or not user.is_active:
        raise AuthError("User not found or inactive")
    return issue_tokens(user)
