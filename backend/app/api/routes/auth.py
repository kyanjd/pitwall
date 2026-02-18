from datetime import timedelta
from typing import Any

from app import crud
from app.api.dependencies import CurrentSession
from app.core import security
from app.core.errors import UnauthorizedError
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=Token)
def login(session: CurrentSession, login_data: LoginRequest) -> Any:
    user = crud.user.get_user_by_email(session=session, email=login_data.email)
    if not user or not security.verify_password(login_data.password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password.")
    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")
