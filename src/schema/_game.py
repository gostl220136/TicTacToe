from pydantic import BaseModel
from typing import List, Optional


class Move(BaseModel):
    player: str
    position: int


class GameBase(BaseModel):
    pass


class GameCreate(GameBase):
    pass


class Game(GameBase):
    id: int
    player_x: str
    player_o: Optional[str]
    board: List[str]
    current_player: str
    status: str
    winner: Optional[str] = None
    moves: List[Move]


class GameList(BaseModel):
    games: List[Game]


class MoveRequest(BaseModel):
    pass  # No body needed, position in URL