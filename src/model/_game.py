from typing import List, Optional
from sqlalchemy import String, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ._base import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_x: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_name"), nullable=False)
    player_o: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("users.user_name"), nullable=True)
    board: Mapped[List[str]] = mapped_column(JSON, default=list)
    current_player: Mapped[str] = mapped_column(String(1), default="X")
    status: Mapped[str] = mapped_column(String(10), default="ongoing")
    winner: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    moves: Mapped[List[dict]] = mapped_column(JSON, default=list)