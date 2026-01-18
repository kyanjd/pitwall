import logging

from app.db.base import Base
from app.db.session import engine
from app.models.user import User

logger = logging.getLogger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


if __name__ == "__main__":
    init_db()
