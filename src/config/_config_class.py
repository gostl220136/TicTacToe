from __future__ import annotations

import json
import os


class Config:

    DB_CONNECTION_STRING: str = "sqlite:///:memory:"
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    __instances: dict[str, Config] = {}

    def __init__(self, file_name: str = ""):
        if file_name in Config.__instances:
            raise RuntimeError("Don't Call constructor!")
        Config.__instances[file_name] = self
        if file_name and os.path.isfile(file_name):
            self._load(file_name)
        else:
            self._connection_string: str = os.getenv('DATABASE_URL', Config.DB_CONNECTION_STRING)
            self._jwt_secret_key: str = os.getenv('JWT_SECRET_KEY', Config.JWT_SECRET_KEY)
            self._jwt_algorithm: str = Config.JWT_ALGORITHM
            self._jwt_access_token_expire_minutes: int = Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    def _load(self, filename: str) -> None:
        with open(filename, "r") as f:
            data = json.load(f)
            self._connection_string = data.get("connection_string", Config.DB_CONNECTION_STRING)
            self._jwt_secret_key = data.get("jwt_secret_key", Config.JWT_SECRET_KEY)
            self._jwt_algorithm = data.get("jwt_algorithm", Config.JWT_ALGORITHM)
            self._jwt_access_token_expire_minutes = data.get("jwt_access_token_expire_minutes", Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def connection_string(self) -> str:
        return self._connection_string

    @property
    def jwt_secret_key(self) -> str:
        return self._jwt_secret_key

    @property
    def jwt_algorithm(self) -> str:
        return self._jwt_algorithm

    @property
    def jwt_access_token_expire_minutes(self) -> int:
        return self._jwt_access_token_expire_minutes

    @classmethod
    def get_instance(cls, file_name: str = "") -> Config:
        if file_name in cls.__instances:
            return cls.__instances[file_name]
        return Config(file_name)
