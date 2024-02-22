from datetime import timedelta, datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from db.core import UserDB
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from starlette import status
from typing import Annotated
from fastapi import Depends

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/token")


class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    email: str
    is_active: bool
    first_name: str
    last_name: str
    role: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=3, max_length=50)
    last_name: str = Field(..., min_length=3, max_length=50)
    role: str = Field(..., min_length=3, max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "username",
                "password": "password",
                "email": "email@email.com",
                "first_name": "name",
                "last_name": "lastname",
                "role": "user"
            }
        }


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=4)


class Token(BaseModel):
    access_token: str
    token_type: str


def create_db_user(user: UserCreate, session: Session):
    existing_username = session.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_username:
        raise ValueError("El nombre de usuario ya están en uso.")
    existing_email = session.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_email:
        raise ValueError("El email ya está en uso.")

    user_db = UserDB(
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=True
    )

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


def authenticate_user(username: str, password: str, db):
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return token


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id,  "role": role}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {"username": username, "id": user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

user_dependency = Annotated[dict, Depends(get_current_user)]
