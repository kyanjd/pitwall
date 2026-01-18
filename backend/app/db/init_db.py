import logging

from sqlmodel import SQLModel

from app.db.session import engine
from app.models.game import Game
from app.models.user import User

logger = logging.getLogger(__name__)


def init_db():
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully.")


if __name__ == "__main__":
    init_db()
