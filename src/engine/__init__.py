from sqlalchemy import Engine, create_engine

from src.config import Config
from src.model import Base


def get_engine(config_file: str = "") -> Engine:
    config = Config.get_instance(config_file)
    engine = create_engine(config.connection_string)
    Base.metadata.create_all(engine)
    return engine


__all__ = [
    "get_engine",
]
