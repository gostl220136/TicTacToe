from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import Response
from sqlalchemy.orm import Session
from src.crud import Crud
from src.engine import get_engine
from src.schema import Token, User, UserCreate, UserUpdate
from src.utils import create_access_token, verify_token
from src.model import User as UserModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

crud = Crud(get_engine())


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user = crud.get_user_by_username(token_data.user_name)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=User, status_code=201, responses={201: {"description": "User created successfully"}})
def register(user_data: UserCreate):
    # Check if user exists
    if crud.get_user_by_username(user_data.user_name):
        raise HTTPException(status_code=400, detail="Username already registered")
    user = crud.create_user(user_data)
    return User(user_name=user.user_name, name=user_data.name)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.user_name})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    return User(user_name=current_user.user_name, name=current_user.entity.name)


@router.put("/me", response_model=User)
def update_current_user(user_update: UserUpdate, current_user: UserModel = Depends(get_current_user)):
    if not crud.update_user(current_user.user_name, user_update.name):
        raise HTTPException(status_code=404, detail="User not found")
    return User(user_name=current_user.user_name, name=user_update.name)