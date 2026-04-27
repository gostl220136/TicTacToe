from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from src.model import Entity, Game, Person, User
from src.schema import EntityBase, GameCreate, UserCreate
from src.utils import get_password_hash, verify_password


class Crud:
    def __init__(self, engine: Engine):
        self._engine: Engine = engine

    # User operations
    def create_user(self, user_data: UserCreate) -> User:
        with Session(self._engine) as session:
            # Create entity first
            entity = Entity(name=user_data.name)
            session.add(entity)
            session.flush()  # Get entity.id

            # Create user
            user = User(
                user_name=user_data.user_name,
                entity_id=entity.id,
                password_hash=get_password_hash(user_data.password)
            )
            session.add(user)
            session.commit()
            stmt = select(User).options(joinedload(User.entity)).where(User.user_name == user.user_name)
            return session.scalar(stmt)

    def get_user_by_username(self, user_name: str) -> Optional[User]:
        with Session(self._engine) as session:
            stmt = select(User).options(joinedload(User.entity)).where(User.user_name == user_name)
            return session.scalar(stmt)

    def authenticate_user(self, user_name: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(user_name)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    # Game operations
    def create_game(self, user_name: str) -> Game:
        with Session(self._engine) as session:
            game = Game(
                player_x=user_name,
                player_o=None,
                board=[""] * 9,
                current_player="X",
                status="waiting",
                moves=[]
            )
            session.add(game)
            session.commit()
            session.refresh(game)
            return game

    def get_available_games(self) -> List[Game]:
        with Session(self._engine) as session:
            stmt = select(Game).where(Game.player_o.is_(None))
            return list(session.scalars(stmt))

    def get_user_games(self, user_name: str) -> List[Game]:
        with Session(self._engine) as session:
            stmt = select(Game).where((Game.player_x == user_name) | (Game.player_o == user_name))
            return list(session.scalars(stmt))

    def delete_game(self, game_id: int, user_name: str) -> bool:
        with Session(self._engine) as session:
            stmt = select(Game).where(Game.id == game_id, ((Game.player_x == user_name) | (Game.player_o == user_name)))
            game = session.scalar(stmt)
            if game and game.status in {"won", "draw"}:
                session.delete(game)
                session.commit()
                return True
            return False

    def update_user(self, user_name: str, new_name: str) -> bool:
        with Session(self._engine) as session:
            stmt = select(User).where(User.user_name == user_name)
            user = session.scalar(stmt)
            if user:
                user.entity.name = new_name
                session.commit()
                return True
            return False

    def delete_user(self, user_name: str) -> bool:
        with Session(self._engine) as session:
            # Check if has games
            stmt = select(Game).where((Game.player_x == user_name) | (Game.player_o == user_name))
            if session.scalars(stmt).first():
                return False  # Can't delete
            stmt = select(User).where(User.user_name == user_name)
            user = session.scalar(stmt)
            if user:
                session.delete(user.entity)
                session.delete(user)
                session.commit()
                return True
            return False

    def get_game(self, game_id: int) -> Optional[Game]:
        with Session(self._engine) as session:
            stmt = select(Game).where(Game.id == game_id)
            return session.scalar(stmt)

    def join_game(self, game_id: int, user_name: str) -> Optional[Game]:
        with Session(self._engine) as session:
            stmt = select(Game).where(Game.id == game_id)
            game = session.scalar(stmt)
            if game and game.player_o is None and game.player_x != user_name:
                game.player_o = user_name
                game.status = "ongoing"
                session.commit()
                session.refresh(game)
                return game
            return None

    def update_game(self, game: Game):
        with Session(self._engine) as session:
            session.merge(game)
            session.commit()

    def make_move(self, game_id: int, position: int, user_name: str) -> Optional[Game]:
        game = self.get_game(game_id)
        if not game:
            raise ValueError("Game not found")
        if game.status != "ongoing":
            raise ValueError("Game is not in progress")
        # Check if user is the current player
        current_player_user = game.player_x if game.current_player == "X" else game.player_o
        if current_player_user != user_name:
            raise ValueError("Not your turn")
        if position < 1 or position > 9:
            raise ValueError("Invalid position")
        if game.board[position - 1] != "":
            raise ValueError("Position already taken")

        game.board[position - 1] = game.current_player
        game.moves.append({"player": game.current_player, "position": position})

        # Check win
        if self._check_win(game.board, game.current_player):
            game.status = "won"
            game.winner = game.current_player
        elif "" not in game.board:
            game.status = "draw"
        else:
            game.current_player = "O" if game.current_player == "X" else "X"

        self.update_game(game)
        return game

    def _check_win(self, board: List[str], player: str) -> bool:
        # Rows
        for i in range(0, 9, 3):
            if all(board[i + j] == player for j in range(3)):
                return True
        # Columns
        for i in range(3):
            if all(board[i + j*3] == player for j in range(3)):
                return True
        # Diagonals
        if all(board[i] == player for i in [0, 4, 8]):
            return True
        if all(board[i] == player for i in [2, 4, 6]):
            return True
        return False

    # Legacy methods (incomplete)
    def get_users(self, filter: str | None = None) -> list[User]:
        if not filter:
            return []
        return []

    def get_persons(self, filter: str | None = None) -> list[Person]:
        if not filter:
            return []
        return []

    def get_entities(self, filter: str | None = None) -> list[Entity]:
        if not filter:
            return []
        return []

    def create_entity(self, new_entity: EntityBase):
        with Session(self._engine) as session:
            assert new_entity
            assert session
