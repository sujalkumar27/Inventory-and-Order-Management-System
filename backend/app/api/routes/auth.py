from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return user_service.register_user(db, data)


@router.post("/login", response_model=TokenPair)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate(db, str(data.email), data.password)
    return user_service.issue_tokens(user)


@router.post("/login/oauth", response_model=TokenPair, include_in_schema=False)
def login_oauth(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """OAuth2 password-flow endpoint so Swagger 'Authorize' works (username=email)."""
    user = user_service.authenticate(db, form.username, form.password)
    return user_service.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return user_service.refresh_tokens(db, data.refresh_token)


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current
