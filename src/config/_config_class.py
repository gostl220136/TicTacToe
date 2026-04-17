from __future__ import annotations

import json
import os


class Config:

    DB_CONNECTION_STRING: str = "sqlite:///:memory:"
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENV_FILE_NAME: str = ".env"

    __instances: dict[str, Config] = {}

    def __init__(self, file_name: str = ""):
        if file_name in Config.__instances:
            raise RuntimeError("Don't Call constructor!")
        Config.__instances[file_name] = self
        if file_name and os.path.isfile(file_name):
            self._load(file_name)
        else:
            self._load_from_environment()

    def _load_from_environment(self) -> None:
        env_values = self._read_env_file(Config.ENV_FILE_NAME)
        self._connection_string: str = os.getenv("DATABASE_URL", env_values.get("DATABASE_URL", Config.DB_CONNECTION_STRING))
        self._jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", env_values.get("JWT_SECRET_KEY", Config.JWT_SECRET_KEY))
        self._jwt_algorithm: str = os.getenv("JWT_ALGORITHM", env_values.get("JWT_ALGORITHM", Config.JWT_ALGORITHM))
        self._jwt_access_token_expire_minutes: int = int(
            os.getenv(
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
                env_values.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            )
        )

    @staticmethod
    def _read_env_file(filename: str) -> dict[str, str]:
        if not os.path.isfile(filename):
            return {}

        env_values: dict[str, str] = {}
        with open(filename, "r", encoding="utf-8") as file_handle:
            for raw_line in file_handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                env_values[key.strip()] = value.strip().strip('"').strip("'")
        return env_values

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
