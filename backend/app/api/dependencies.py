from typing import Annotated

from app.db.session import get_session_local as get_session
from fastapi.params import Depends
from sqlmodel import Session

CurrentSession = Annotated[Session, Depends(get_session)]


def get_current_user():
    pass
