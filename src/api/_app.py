from fastapi import FastAPI

from ._routes import define_routes

_app: FastAPI | None = None


def build_app():
    global _app
    if not _app:
        _app = FastAPI(
            title="TicTacToe Game API",
            version="1.0.0",
            description="REST API for authenticated TicTacToe gameplay with persistent game history.",
        )
        define_routes(_app)

    return _app
