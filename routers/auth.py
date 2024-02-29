from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from db.user import UserCreate, create_db_user, authenticate_user, Token, create_access_token
from db.core import get_db
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/api",
    tags=["Auth"],
)


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: UserCreate, db: Session = Depends(get_db)):
    try:
        user_db = create_db_user(create_user_request, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user_db


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    return {"access_token": token, "token_type": "bearer"}
