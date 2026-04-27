from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from src.api._auth import get_current_user
from src.crud import Crud
from src.engine import get_engine
from src.schema import Game, GameList

router = APIRouter()
crud = Crud(get_engine())


@router.post(
    "/games",
    response_model=Game,
    status_code=201,
    summary="Create a new game",
    description="Create a new TicTacToe game. The authenticated user is assigned as player X.",
    responses={201: {"description": "Game created successfully"}},
)
def create_game(current_user=Depends(get_current_user)):
    game = crud.create_game(current_user.user_name)
    return Game(
        id=game.id,
        player_x=game.player_x,
        player_o=game.player_o,
        board=game.board,
        current_player=game.current_player,
        status=game.status,
        winner=game.winner,
        moves=game.moves
    )


@router.get(
    "/games",
    response_model=GameList,
    summary="List games for current user",
    description="Return all games where the authenticated user is player X or player O.",
)
def get_games(current_user=Depends(get_current_user)):
    games = crud.get_user_games(current_user.user_name)
    game_list = [
        Game(
            id=g.id,
            player_x=g.player_x,
            player_o=g.player_o,
            board=g.board,
            current_player=g.current_player,
            status=g.status,
            winner=g.winner,
            moves=g.moves
        ) for g in games
    ]
    return GameList(games=game_list)


@router.get(
    "/games/available",
    response_model=GameList,
    summary="List joinable games",
    description="Return games waiting for a second player for the authenticated user.",
)
def get_available_games(current_user=Depends(get_current_user)):
    assert current_user
    games = crud.get_available_games()
    game_list = [
        Game(
            id=g.id,
            player_x=g.player_x,
            player_o=g.player_o,
            board=g.board,
            current_player=g.current_player,
            status=g.status,
            winner=g.winner,
            moves=g.moves
        ) for g in games
    ]
    return GameList(games=game_list)


@router.get(
    "/games/{game_id}",
    response_model=Game,
    summary="Get game by ID",
    description="Return one game including board, status, winner, and move history.",
)
def get_game(game_id: int, current_user=Depends(get_current_user)):
    game = crud.get_game(game_id)
    if not game or (game.player_x != current_user.user_name and game.player_o != current_user.user_name):
        raise HTTPException(status_code=404, detail="Game not found")
    return Game(
        id=game.id,
        player_x=game.player_x,
        player_o=game.player_o,
        board=game.board,
        current_player=game.current_player,
        status=game.status,
        winner=game.winner,
        moves=game.moves
    )


@router.post(
    "/games/{game_id}/join",
    response_model=Game,
    summary="Join a waiting game",
    description="Join a game as player O if it is waiting for an opponent.",
)
def join_game(game_id: int, current_user=Depends(get_current_user)):
    game = crud.join_game(game_id, current_user.user_name)
    if not game:
        raise HTTPException(status_code=400, detail="Cannot join this game")
    return Game(
        id=game.id,
        player_x=game.player_x,
        player_o=game.player_o,
        board=game.board,
        current_player=game.current_player,
        status=game.status,
        winner=game.winner,
        moves=game.moves
    )


@router.put(
    "/games/{game_id}/move/{position}",
    response_model=Game,
    summary="Make a move",
    description="Make a move in the given game at position 1-9. Handles wins, draws, and invalid moves.",
)
def make_move(game_id: int, position: int, current_user=Depends(get_current_user)):
    game = crud.get_game(game_id)
    if not game or (game.player_x != current_user.user_name and game.player_o != current_user.user_name):
        raise HTTPException(status_code=404, detail="Game not found")
    if position < 1 or position > 9:
        raise HTTPException(status_code=400, detail="Invalid position")
    try:
        game = crud.make_move(game_id, position, current_user.user_name)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    if not game:
        raise HTTPException(status_code=400, detail="Invalid move")
    return Game(
        id=game.id,
        player_x=game.player_x,
        player_o=game.player_o,
        board=game.board,
        current_player=game.current_player,
        status=game.status,
        winner=game.winner,
        moves=game.moves
    )


@router.delete(
    "/games/{game_id}",
    status_code=204,
    summary="Delete a completed game",
    description="Delete a game that is completed (won or draw) and belongs to the authenticated user.",
)
def delete_game(game_id: int, current_user=Depends(get_current_user)):
    success = crud.delete_game(game_id, current_user.user_name)
    if not success:
        raise HTTPException(status_code=400, detail="Game not found, not authorized, or not completed")
    return Response(status_code=204)