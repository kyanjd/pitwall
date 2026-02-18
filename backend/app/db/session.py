from contextlib import contextmanager

from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)


@contextmanager
def get_session_local():
    with Session(engine) as session:
        yield session


def get_session():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    from sqlalchemy import text
    from sqlmodel import SQLModel, delete

    from app.models.f1 import Circuit

    # with Session(engine) as session:a
    #     session.exec(delete(Circuit))
    #     session.commit()

    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
