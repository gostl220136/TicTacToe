from fastapi import FastAPI

from ._auth import router as auth_router
from ._export import router as export_router
from ._games import router as games_router


def define_routes(app: FastAPI) -> None:
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(games_router, tags=["games"])
    app.include_router(export_router, prefix="/export", tags=["export"])

    @app.get("/")
    def get_root():
        return {"message": "TicTacToe API"}

    assert get_root
