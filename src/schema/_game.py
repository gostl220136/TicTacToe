from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class Move(BaseModel):
    player: str = Field(description="Symbol of the player who made the move (X or O)", examples=["X"])
    position: int = Field(description="Board position from 1 to 9", ge=1, le=9, examples=[5])


class GameBase(BaseModel):
    pass


class GameCreate(GameBase):
    pass


class Game(GameBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "player_x": "alice",
                "player_o": "bob",
                "board": ["X", "O", "", "", "X", "", "", "", "O"],
                "current_player": "X",
                "status": "ongoing",
                "winner": None,
                "moves": [
                    {"player": "X", "position": 1},
                    {"player": "O", "position": 2},
                    {"player": "X", "position": 5},
                    {"player": "O", "position": 9},
                ],
            }
        }
    )

    id: int = Field(description="Game identifier", examples=[1])
    player_x: str = Field(description="Username of player X", examples=["alice"])
    player_o: Optional[str] = Field(default=None, description="Username of player O", examples=["bob"])
    board: List[str] = Field(description="Board state with 9 entries. Empty string means free position.")
    current_player: str = Field(description="Current symbol to move (X or O)", examples=["X"])
    status: str = Field(description="Game status: waiting, ongoing, won, draw", examples=["ongoing"])
    winner: Optional[str] = Field(default=None, description="Winner symbol (X/O) for won games")
    moves: List[Move] = Field(description="Move history in chronological order")


class GameList(BaseModel):
    games: List[Game] = Field(description="List of games")


class MoveRequest(BaseModel):
    pass  # No body needed, position in URL