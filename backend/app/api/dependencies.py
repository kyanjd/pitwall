import uuid
from typing import Annotated

import jwt
from app import crud
from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.core.security import ALGORITHM
from app.db.session import get_session
from app.models.user import User
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session

CurrentSession = Annotated[Session, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    session: CurrentSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: uuid.UUID | None = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid token.")
    except InvalidTokenError:
        raise UnauthorizedError("Invalid token.")

    user = crud.user.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise UnauthorizedError("User not found.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
