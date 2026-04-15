from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    user_name: str = Field(min_length=3, max_length=50, description="Unique username", examples=["alice"])


class UserCreate(UserBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_name": "alice",
                "password": "strong-password",
                "name": "Alice Example",
            }
        }
    )

    password: str = Field(min_length=4, description="Plain password that is hashed before storage")
    name: str = Field(min_length=1, max_length=100, description="Display name", examples=["Alice Example"])


class UserLogin(UserBase):
    password: str = Field(min_length=4, description="Password used for login")


class User(UserBase):
    name: str = Field(description="Display name", examples=["Alice Example"])


class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="New display name", examples=["Alice Updated"])


class Token(BaseModel):
    access_token: str = Field(description="JWT Bearer token")
    token_type: str = Field(description="Authentication scheme", examples=["bearer"])


class TokenData(BaseModel):
    user_name: str | None = None