import uuid

from sqlmodel import Session, select

from app.core.errors import ForbiddenError, NotFoundError
from app.models.game import Game, GameCreate, GameUser
from app.models.user import User, UserPublic


def create_game(*, session: Session, game_create: GameCreate, created_by: uuid.UUID) -> Game:
    db_obj = Game(
        name=game_create.name,
        created_by=created_by,
    )
    session.add(db_obj)
    add_user_to_game(session=session, game_id=db_obj.id, user_id=created_by)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_game_by_invite_code(*, session: Session, invite_code: str) -> Game:
    statement = select(Game).where(Game.invite_code == invite_code)
    game = session.exec(statement).first()
    if not game:
        raise NotFoundError(f"Game {invite_code} not found")
    return game


def join_game(*, session: Session, invite_code: str, user_id: uuid.UUID) -> Game:
    game = get_game_by_invite_code(session=session, invite_code=invite_code)
    already_member = session.get(GameUser, (game.id, user_id))
    if not already_member:
        add_user_to_game(session=session, game_id=game.id, user_id=user_id)
        session.commit()
    return game


def add_user_to_game(*, session: Session, game_id: uuid.UUID, user_id: uuid.UUID) -> None:
    game_user = GameUser(game_id=game_id, user_id=user_id)
    session.add(game_user)


def get_game_by_id(*, session: Session, game_id: uuid.UUID, user_id: uuid.UUID) -> Game:
    game = session.get(Game, game_id)
    if not game:
        raise NotFoundError(f"Game {game_id} not found")
    is_member = session.get(GameUser, (game.id, user_id))
    if not is_member:
        raise ForbiddenError(f"User {user_id} is not a member of game {game_id}")
    return game


def get_game_by_id_with_members(
    *, session: Session, game_id: uuid.UUID, user_id: uuid.UUID
) -> tuple[Game, list[UserPublic]]:
    game = get_game_by_id(session=session, game_id=game_id, user_id=user_id)
    game_users = session.exec(select(GameUser).where(GameUser.game_id == game_id)).all()
    members = []
    for game_user in game_users:
        user = session.get(User, game_user.user_id)
        if user:
            members.append(UserPublic(name=user.name, email=user.email, id=user.id))
    return game, members


def get_games_by_user(*, session: Session, user_id: uuid.UUID) -> list[Game]:
    game_users = session.exec(select(GameUser).where(GameUser.user_id == user_id)).all()
    games = []
    for game_user in game_users:
        game = session.get(Game, game_user.game_id)
        if game:
            games.append(game)
    return games
