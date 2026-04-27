import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from src.crud import Crud
from src.model import Base
from src.schema import UserCreate


@pytest.fixture
def crud() -> Crud:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Crud(engine)


def _create_user(crud: Crud, user_name: str, password: str = "Kennwort2", name: str = "Bob"):
    return crud.create_user(
        UserCreate(
            user_name=user_name,
            password=password,
            name=name,
        )
    )


def test_crud_00_init(crud: Crud):
    assert crud


def test_crud_01_create_user_hashes_password(crud: Crud):
    user = _create_user(crud, "user123", password="MySecret123")

    assert user.user_name == "user123"
    assert user.entity.name == "Bob"
    assert user.password_hash != "MySecret123"


def test_crud_02_get_user_by_username_found_and_missing(crud: Crud):
    _create_user(crud, "user123")

    assert crud.get_user_by_username("user123") is not None
    assert crud.get_user_by_username("unknown") is None


def test_crud_03_authenticate_user_success_and_failures(crud: Crud):
    _create_user(crud, "user123", password="GoodPass1")

    assert crud.authenticate_user("user123", "GoodPass1") is not None
    assert crud.authenticate_user("user123", "WrongPass") is None
    assert crud.authenticate_user("nobody", "GoodPass1") is None


def test_crud_04_update_user_success_and_missing_user(crud: Crud):
    _create_user(crud, "user123", name="Original")

    assert crud.update_user("user123", "Updated") is True
    assert crud.get_user_by_username("user123").entity.name == "Updated"
    assert crud.update_user("ghost", "Nobody") is False


def test_crud_05_create_and_join_game(crud: Crud):
    _create_user(crud, "alice")
    _create_user(crud, "bob")

    game = crud.create_game("alice")
    assert game.player_x == "alice"
    assert game.player_o is None
    assert game.status == "waiting"
    assert game.current_player == "X"
    assert game.board == [""] * 9

    joined = crud.join_game(game.id, "bob")
    assert joined is not None
    assert joined.player_o == "bob"
    assert joined.status == "ongoing"


def test_crud_06_join_game_rejects_invalid_join(crud: Crud):
    _create_user(crud, "alice")
    _create_user(crud, "bob")
    _create_user(crud, "charlie")

    game = crud.create_game("alice")

    assert crud.join_game(game.id, "alice") is None
    assert crud.join_game(9999, "bob") is None

    assert crud.join_game(game.id, "bob") is not None
    assert crud.join_game(game.id, "charlie") is None


def test_crud_07_get_available_games_and_user_games(crud: Crud):
    _create_user(crud, "alice")
    _create_user(crud, "bob")

    waiting_game = crud.create_game("alice")
    joined_game = crud.create_game("bob")
    assert crud.join_game(joined_game.id, "alice") is not None

    available_ids = {game.id for game in crud.get_available_games()}
    assert waiting_game.id in available_ids
    assert joined_game.id not in available_ids

    alice_games = {game.id for game in crud.get_user_games("alice")}
    bob_games = {game.id for game in crud.get_user_games("bob")}
    assert waiting_game.id in alice_games
    assert joined_game.id in alice_games
    assert joined_game.id in bob_games


def test_crud_08_delete_game_requires_finished_status_and_membership(crud: Crud):
    _create_user(crud, "alice")
    _create_user(crud, "bob")
    _create_user(crud, "charlie")

    game = crud.create_game("alice")
    assert crud.join_game(game.id, "bob") is not None

    assert crud.delete_game(game.id, "alice") is False

    game_for_update = crud.get_game(game.id)
    game_for_update.status = "won"
    game_for_update.winner = "X"
    crud.update_game(game_for_update)

    assert crud.delete_game(game.id, "charlie") is False
    assert crud.delete_game(game.id, "alice") is True
    assert crud.get_game(game.id) is None


def test_crud_09_delete_user_blocked_when_games_exist(crud: Crud):
    _create_user(crud, "alice")
    _create_user(crud, "bob")

    game = crud.create_game("alice")
    assert crud.join_game(game.id, "bob") is not None

    assert crud.delete_user("alice") is False


def test_crud_10_delete_user_without_games(crud: Crud):
    _create_user(crud, "alice")

    assert crud.delete_user("alice") is True
    assert crud.get_user_by_username("alice") is None


def test_crud_11_make_move_validations_and_turns(crud: Crud):
    _create_user(crud, "alice")
    _create_user(crud, "bob")

    game = crud.create_game("alice")

    with pytest.raises(ValueError, match="Game is not in progress"):
        crud.make_move(game.id, 1, "alice")

    with pytest.raises(ValueError, match="Game not found"):
        crud.make_move(9999, 1, "alice")

    assert crud.join_game(game.id, "bob") is not None

    with pytest.raises(ValueError, match="Not your turn"):
        crud.make_move(game.id, 1, "bob")

    with pytest.raises(ValueError, match="Invalid position"):
        crud.make_move(game.id, 0, "alice")

    game_after_first = crud.make_move(game.id, 1, "alice")
    assert game_after_first.board[0] == "X"
    assert game_after_first.current_player == "O"

    with pytest.raises(ValueError, match="Position already taken"):
        crud.make_move(game.id, 1, "bob")


def test_crud_12_make_move_can_win_game(crud: Crud):
    _create_user(crud, "alice")
    _create_user(crud, "bob")

    game = crud.create_game("alice")
    assert crud.join_game(game.id, "bob") is not None

    crud.make_move(game.id, 1, "alice")
    crud.make_move(game.id, 4, "bob")
    crud.make_move(game.id, 2, "alice")
    crud.make_move(game.id, 5, "bob")
    result = crud.make_move(game.id, 3, "alice")

    assert result.status == "won"
    assert result.winner == "X"
    assert result.board[0:3] == ["X", "X", "X"]
