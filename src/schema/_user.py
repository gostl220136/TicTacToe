from pydantic import BaseModel


class UserBase(BaseModel):
    user_name: str


class UserCreate(UserBase):
    password: str
    name: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    name: str


class UserUpdate(BaseModel):
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_name: str | None = None