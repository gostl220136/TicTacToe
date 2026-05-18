from datetime import datetime
from xml.etree import ElementTree as ET

from fastapi.testclient import TestClient

from .conftest import get_token


def _create_completed_game(client: TestClient, user_x: str, user_o: str):
    token_x = get_token(client, user_x, "pass", user_x.title())
    token_o = get_token(client, user_o, "pass", user_o.title())
    game_id = client.post("/games", headers={"Authorization": f"Bearer {token_x}"}).json()["id"]
    client.post(f"/games/{game_id}/join", headers={"Authorization": f"Bearer {token_o}"})

    moves = [
        (token_x, 1),
        (token_o, 4),
        (token_x, 2),
        (token_o, 5),
        (token_x, 3),
    ]
    for token, position in moves:
        client.put(f"/games/{game_id}/move/{position}", headers={"Authorization": f"Bearer {token}"})

    return game_id, token_x


def test_export_xml_returns_downloadable_xml(client: TestClient) -> None:
    game_id, token_x = _create_completed_game(client, "export_x1", "export_o1")

    resp = client.get("/api/export/xml", headers={"Authorization": f"Bearer {token_x}"})

    assert resp.status_code == 200
    assert resp.headers["content-disposition"] == 'attachment; filename="tictactoe-export.xml"'

    root = ET.fromstring(resp.content)
    assert root.tag == "ticTacToeExport"

    games_element = root.find("games")
    assert games_element is not None

    game_element = games_element.find(f"./game[@id='{game_id}']")
    assert game_element is not None
    assert game_element.attrib["status"] == "won"
    assert game_element.attrib["currentPlayer"] == "X"

    players_element = game_element.find("players")
    assert players_element is not None
    players = {(player.attrib["role"], player.attrib["username"]) for player in players_element.findall("player")}
    assert ("X", "export_x1") in players
    assert ("O", "export_o1") in players

    winner_element = game_element.find("winner")
    assert winner_element is not None
    assert winner_element.attrib["symbol"] == "X"
    assert winner_element.attrib["username"] == "export_x1"

    created_at_text = game_element.findtext("createdAt")
    assert created_at_text is not None
    datetime.fromisoformat(created_at_text)

    board_cells = game_element.findall("./board/cell")
    assert len(board_cells) == 9
    assert [cell.text for cell in board_cells[:3]] == ["X", "X", "X"]

    moves = game_element.findall("./moves/move")
    assert len(moves) == 5
    assert moves[0].attrib == {"order": "1", "player": "X", "position": "1"}


def test_export_xml_requires_authentication(client: TestClient) -> None:
    resp = client.get("/api/export/xml")
    assert resp.status_code == 401


def test_export_single_game_by_id(client: TestClient) -> None:
    game_id, token_x = _create_completed_game(client, "single_x1", "single_o1")

    resp = client.get(f"/api/export/xml/{game_id}", headers={"Authorization": f"Bearer {token_x}"})
    assert resp.status_code == 200
    assert resp.headers["content-disposition"] == f'attachment; filename="tictactoe-export-{game_id}.xml"'

    root = ET.fromstring(resp.content)
    game_element = root.find("games").find(f"game")
    assert game_element is not None
    assert game_element.attrib["id"] == str(game_id)


def test_export_single_game_not_found(client: TestClient) -> None:
    token = get_token(client, "export_none", "pass", "Export None")
    resp = client.get("/api/export/xml/999999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404