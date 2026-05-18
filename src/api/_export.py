from xml.etree import ElementTree as ET

from fastapi import APIRouter, Depends
from starlette.responses import Response

from src.api._auth import get_current_user
from src.api._games import serialize_game
from src.crud import Crud
from src.engine import get_engine


router = APIRouter()
crud = Crud(get_engine())


def _append_text_element(parent: ET.Element, tag: str, text: str | None) -> ET.Element:
    element = ET.SubElement(parent, tag)
    if text is not None:
        element.text = text
    return element


def _build_export_xml() -> str:
    games = crud.get_export_games()

    root = ET.Element("ticTacToeExport")
    games_element = ET.SubElement(root, "games", count=str(len(games)))

    for game in games:
        game_schema = serialize_game(game)
        game_element = ET.SubElement(
            games_element,
            "game",
            id=str(game_schema.id),
            status=game_schema.status,
            currentPlayer=game_schema.current_player,
        )

        players_element = ET.SubElement(game_element, "players")
        ET.SubElement(players_element, "player", role="X", username=game_schema.player_x)
        if game_schema.player_o:
            ET.SubElement(players_element, "player", role="O", username=game_schema.player_o)

        winner_element = ET.SubElement(game_element, "winner")
        if game_schema.winner:
            winner_element.set("symbol", game_schema.winner)
            winner_user = game_schema.player_x if game_schema.winner == "X" else game_schema.player_o
            if winner_user:
                winner_element.set("username", winner_user)

        _append_text_element(game_element, "createdAt", game_schema.created_at.isoformat())

        board_element = ET.SubElement(game_element, "board")
        for index, cell in enumerate(game_schema.board, start=1):
            board_cell = ET.SubElement(board_element, "cell", index=str(index))
            board_cell.text = cell

        moves_element = ET.SubElement(game_element, "moves")
        for order, move in enumerate(game_schema.moves, start=1):
            ET.SubElement(
                moves_element,
                "move",
                order=str(order),
                player=move.player,
                position=str(move.position),
            )

    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")


@router.get(
    "/xml",
    summary="Export all games as XML",
    description="Export all TicTacToe games from the database as a downloadable XML document.",
)
def export_xml(current_user=Depends(get_current_user)):
    assert current_user
    xml_content = _build_export_xml()
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={"Content-Disposition": 'attachment; filename="tictactoe-export.xml"'},
    )