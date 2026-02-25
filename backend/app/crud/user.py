import uuid

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models.user import User, UserCreate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User(
        name=user_create.name,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> User | None:
    return session.get(User, user_id)


def update_password(*, session: Session, user: User, new_hashed_password: str) -> None:
    user.hashed_password = new_hashed_password
    session.add(user)
    session.commit()


def update_name(*, session: Session, user: User, name: str) -> User:
    user.name = name
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
