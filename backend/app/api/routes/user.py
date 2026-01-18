from typing import Any

from app import crud
from app.api.dependencies import CurrentSession
from app.core.errors import AlreadyExistsError
from app.models.user import UserCreate, UserPublic
from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", response_model=UserPublic)
def create_user(session: CurrentSession, user_create: UserCreate) -> Any:
    user = crud.user.get_user_by_email(session=session, email=user_create.email)
    if user:
        raise AlreadyExistsError(f"User with email {user_create.email} already exists.")
    user = crud.user.create_user(session=session, user_create=user_create)
    return user
