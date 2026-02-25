from typing import Any

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.core import security
from app.core.errors import AlreadyExistsError, UnauthorizedError
from app.models.user import PasswordChange, UserCreate, UserPublic, UserUpdate
from fastapi import APIRouter, Response

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", response_model=UserPublic)
def create_user(session: CurrentSession, user_create: UserCreate) -> UserPublic:
    user = crud.user.get_user_by_email(session=session, email=user_create.email)
    if user:
        raise AlreadyExistsError(f"User with email {user_create.email} already exists.")
    user = crud.user.create_user(session=session, user_create=user_create)
    return UserPublic.model_validate(user)


@router.get("/me", response_model=UserPublic)
def get_me(current_user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.patch("/me", response_model=UserPublic)
def update_me(session: CurrentSession, current_user: CurrentUser, user_update: UserUpdate) -> UserPublic:
    user = crud.user.update_name(session=session, user=current_user, name=user_update.name)
    return UserPublic.model_validate(user)


@router.put("/me/password", status_code=204)
def change_password(
    session: CurrentSession, current_user: CurrentUser, password_change: PasswordChange
) -> Response:
    if not security.verify_password(password_change.current_password, current_user.hashed_password):
        raise UnauthorizedError("Current password is incorrect.")
    new_hash = security.get_password_hash(password_change.new_password)
    crud.user.update_password(session=session, user=current_user, new_hashed_password=new_hash)
    return Response(status_code=204)
