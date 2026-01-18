import os

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
