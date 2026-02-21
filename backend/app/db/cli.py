import argparse
import logging

from sqlalchemy import text
from sqlmodel import SQLModel

from app.db.session import engine
from app.models.f1 import Circuit, Constructor, Driver, F1Session, Race, Result
from app.models.game import Game, GameUser
from app.models.user import User

logger = logging.getLogger(__name__)


def create_tables():
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created.")


def drop_tables(force: bool):
    if not force:
        raise RuntimeError("Refusing to drop tables without --force")

    SQLModel.metadata.drop_all(engine)
    logger.warning("Database tables dropped (ORM-managed only).")


def reset_tables(force: bool):
    if not force:
        raise RuntimeError("Refusing to reset tables without --force")

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    logger.warning("Database tables reset.")


def nuke_database(force: bool):
    if not force:
        raise RuntimeError("Refusing to NUKE database without --force. This will DROP SCHEMA public CASCADE.")

    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))

    logger.critical("DATABASE NUKED: public schema dropped and recreated.")


def main():
    parser = argparse.ArgumentParser(description="Database management CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("create", help="Create all database tables")

    drop_parser = subparsers.add_parser("drop", help="Drop ORM-managed tables only")
    drop_parser.add_argument("--force", action="store_true")

    reset_parser = subparsers.add_parser("reset", help="Drop and recreate ORM-managed tables")
    reset_parser.add_argument("--force", action="store_true")

    nuke_parser = subparsers.add_parser(
        "nuke",
        help="DROP SCHEMA public CASCADE (DANGEROUS, DEV ONLY)",
    )
    nuke_parser.add_argument("--force", action="store_true")

    args = parser.parse_args()

    try:
        if args.command == "create":
            create_tables()
        elif args.command == "drop":
            drop_tables(force=args.force)
        elif args.command == "reset":
            reset_tables(force=args.force)
        elif args.command == "nuke":
            nuke_database(force=args.force)
        else:
            parser.print_help()
    except Exception as e:
        logger.error(str(e))


if __name__ == "__main__":
    main()
