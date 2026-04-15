"""
Unit tests for game management API endpoints:
  POST /games                       – create a game
  GET  /games                       – list my games
  GET  /games/available             – list joinable games
  GET  /games/{game_id}             – get a specific game
  POST /games/{game_id}/join        – join a waiting game
  PUT  /games/{game_id}/move/{pos}  – make a move
  DELETE /games/{game_id}           – delete a game
"""
from fastapi.testclient import TestClient

from .conftest import get_token


# ---------------------------------------------------------------------------
# POST /games
# ---------------------------------------------------------------------------

def test_create_game_success(client: TestClient) -> None:
    """Authenticated user can create a game (status 201)."""
    token = get_token(client, "g_creator1", "pass", "Creator One")
    resp = client.post("/games", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["player_x"] == "g_creator1"
    assert data["player_o"] is None
    assert data["status"] == "waiting"
    assert data["board"] == [""] * 9


def test_create_game_unauthenticated(client: TestClient) -> None:
    """Creating a game without a token returns 401."""
    resp = client.post("/games")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /games
# ---------------------------------------------------------------------------

def test_get_games_returns_own_games(client: TestClient) -> None:
    """GET /games lists games that belong to the current user."""
    token = get_token(client, "g_lister1", "pass", "Lister One")
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/games", headers=headers)
    resp = client.get("/games", headers=headers)
    assert resp.status_code == 200
    games = resp.json()["games"]
    assert any(g["player_x"] == "g_lister1" for g in games)


def test_get_games_unauthenticated(client: TestClient) -> None:
    resp = client.get("/games")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /games/available
# ---------------------------------------------------------------------------

def test_get_available_games(client: TestClient) -> None:
    """GET /games/available returns games with no second player."""
    token = get_token(client, "g_avail1", "pass", "Avail One")
    client.post("/games", headers={"Authorization": f"Bearer {token}"})
    resp = client.get("/games/available")
    assert resp.status_code == 200
    games = resp.json()["games"]
    for g in games:
        assert g["player_o"] is None


# ---------------------------------------------------------------------------
# GET /games/{game_id}
# ---------------------------------------------------------------------------

def test_get_game_by_id(client: TestClient) -> None:
    """Owner can retrieve their game by id."""
    token = get_token(client, "g_get1", "pass", "Get One")
    headers = {"Authorization": f"Bearer {token}"}
    game_id = client.post("/games", headers=headers).json()["id"]
    resp = client.get(f"/games/{game_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == game_id


def test_get_game_not_found(client: TestClient) -> None:
    """Requesting a non-existent game returns 404."""
    token = get_token(client, "g_get2", "pass", "Get Two")
    resp = client.get("/games/999999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_get_game_other_player_forbidden(client: TestClient) -> None:
    """A user that is not part of the game gets 404."""
    token_a = get_token(client, "g_getA", "pass", "Get A")
    token_b = get_token(client, "g_getB", "pass", "Get B")
    game_id = client.post("/games", headers={"Authorization": f"Bearer {token_a}"}).json()["id"]
    resp = client.get(f"/games/{game_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /games/{game_id}/join
# ---------------------------------------------------------------------------

def test_join_game_success(client: TestClient) -> None:
    """A second user can join a waiting game."""
    token_x = get_token(client, "g_joinX", "pass", "Join X")
    token_o = get_token(client, "g_joinO", "pass", "Join O")
    game_id = client.post("/games", headers={"Authorization": f"Bearer {token_x}"}).json()["id"]
    resp = client.post(f"/games/{game_id}/join", headers={"Authorization": f"Bearer {token_o}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["player_o"] == "g_joinO"
    assert data["status"] == "ongoing"


def test_join_own_game_fails(client: TestClient) -> None:
    """The creator cannot join their own game."""
    token = get_token(client, "g_joinSelf", "pass", "Join Self")
    game_id = client.post("/games", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    resp = client.post(f"/games/{game_id}/join", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400


def test_join_game_unauthenticated(client: TestClient) -> None:
    token = get_token(client, "g_joinAnon", "pass", "Join Anon")
    game_id = client.post("/games", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    resp = client.post(f"/games/{game_id}/join")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PUT /games/{game_id}/move/{position}
# ---------------------------------------------------------------------------

def _create_ongoing_game(client, user_x: str, user_o: str):
    """Helper: create a game and have user_o join it. Returns (game_id, token_x, token_o)."""
    token_x = get_token(client, user_x, "pass", user_x)
    token_o = get_token(client, user_o, "pass", user_o)
    game_id = client.post("/games", headers={"Authorization": f"Bearer {token_x}"}).json()["id"]
    client.post(f"/games/{game_id}/join", headers={"Authorization": f"Bearer {token_o}"})
    return game_id, token_x, token_o


def test_make_move_success(client: TestClient) -> None:
    """Player X can make the first move."""
    game_id, token_x, _ = _create_ongoing_game(client, "mv_x1", "mv_o1")
    resp = client.put(
        f"/games/{game_id}/move/1",
        headers={"Authorization": f"Bearer {token_x}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["board"][0] == "X"
    assert data["current_player"] == "O"


def test_make_move_not_your_turn(client: TestClient) -> None:
    """Player O cannot move when it is X's turn."""
    game_id, _, token_o = _create_ongoing_game(client, "mv_x2", "mv_o2")
    resp = client.put(
        f"/games/{game_id}/move/1",
        headers={"Authorization": f"Bearer {token_o}"},
    )
    assert resp.status_code == 400


def test_make_move_position_already_taken(client: TestClient) -> None:
    """Moving to an occupied position returns 400."""
    game_id, token_x, token_o = _create_ongoing_game(client, "mv_x3", "mv_o3")
    client.put(f"/games/{game_id}/move/5", headers={"Authorization": f"Bearer {token_x}"})
    resp = client.put(
        f"/games/{game_id}/move/5",
        headers={"Authorization": f"Bearer {token_o}"},
    )
    assert resp.status_code == 400


def test_make_move_out_of_bounds(client: TestClient) -> None:
    """Position outside 1-9 returns 400."""
    game_id, token_x, _ = _create_ongoing_game(client, "mv_x4", "mv_o4")
    resp = client.put(
        f"/games/{game_id}/move/10",
        headers={"Authorization": f"Bearer {token_x}"},
    )
    assert resp.status_code == 400


def test_make_move_unauthenticated(client: TestClient) -> None:
    game_id, _, _ = _create_ongoing_game(client, "mv_x5", "mv_o5")
    resp = client.put(f"/games/{game_id}/move/1")
    assert resp.status_code == 401


def test_win_condition(client: TestClient) -> None:
    """X wins by filling the top row (positions 1,2,3)."""
    game_id, token_x, token_o = _create_ongoing_game(client, "win_x1", "win_o1")
    moves = [
        (token_x, 1), (token_o, 4),
        (token_x, 2), (token_o, 5),
        (token_x, 3),  # X wins
    ]
    for token, pos in moves:
        resp = client.put(
            f"/games/{game_id}/move/{pos}",
            headers={"Authorization": f"Bearer {token}"},
        )
    data = resp.json()
    assert data["status"] == "won"
    assert data["winner"] == "X"


def test_draw_condition(client: TestClient) -> None:
    """A fully filled board with no winner results in a draw."""
    game_id, token_x, token_o = _create_ongoing_game(client, "draw_x1", "draw_o1")
    # Board that ends in a draw:
    # X O X
    # X X O
    # O X O
    moves = [
        (token_x, 1), (token_o, 2),
        (token_x, 3), (token_o, 6),
        (token_x, 4), (token_o, 7),
        (token_x, 5), (token_o, 9),
        (token_x, 8),
    ]
    for token, pos in moves:
        resp = client.put(
            f"/games/{game_id}/move/{pos}",
            headers={"Authorization": f"Bearer {token}"},
        )
    data = resp.json()
    assert data["status"] == "draw"
    assert data["winner"] is None


# ---------------------------------------------------------------------------
# DELETE /games/{game_id}
# ---------------------------------------------------------------------------

def test_delete_game_success(client: TestClient) -> None:
    """The owner can delete their own completed game."""
    game_id, token_x, token_o = _create_ongoing_game(client, "del_x1", "del_o1")
    moves = [
        (token_x, 1), (token_o, 4),
        (token_x, 2), (token_o, 5),
        (token_x, 3),
    ]
    for token, pos in moves:
        client.put(f"/games/{game_id}/move/{pos}", headers={"Authorization": f"Bearer {token}"})

    headers = {"Authorization": f"Bearer {token_x}"}
    resp = client.delete(f"/games/{game_id}", headers=headers)
    assert resp.status_code == 204
    # Confirm it's gone
    assert client.get(f"/games/{game_id}", headers=headers).status_code == 404


def test_delete_game_not_owner(client: TestClient) -> None:
    """A user that does not own the game cannot delete it."""
    game_id, token_owner, token_other_player = _create_ongoing_game(client, "del_owner2", "del_player2")
    token_other = get_token(client, "del_other2", "pass", "Del Other 2")

    # Finish game first (owner wins)
    moves = [
        (token_owner, 1), (token_other_player, 4),
        (token_owner, 2), (token_other_player, 5),
        (token_owner, 3),
    ]
    for token, pos in moves:
        client.put(f"/games/{game_id}/move/{pos}", headers={"Authorization": f"Bearer {token}"})

    resp = client.delete(f"/games/{game_id}", headers={"Authorization": f"Bearer {token_other}"})
    assert resp.status_code == 400


def test_delete_game_unauthenticated(client: TestClient) -> None:
    token = get_token(client, "del_anon3", "pass", "Del Anon 3")
    game_id = client.post("/games", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    resp = client.delete(f"/games/{game_id}")
    assert resp.status_code == 401


def test_delete_game_not_completed(client: TestClient) -> None:
    """Deleting a waiting or ongoing game is rejected."""
    token = get_token(client, "del_waiting1", "pass", "Del Waiting")
    headers = {"Authorization": f"Bearer {token}"}
    game_id = client.post("/games", headers=headers).json()["id"]
    resp = client.delete(f"/games/{game_id}", headers=headers)
    assert resp.status_code == 400
