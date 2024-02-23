from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.core import get_db
from db.user import user_dependency, UserDB, UserVerification, bcrypt_context
from starlette import status

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(UserDB).filter(UserDB.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user_verification: UserVerification, user: user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_db = db.query(UserDB).filter(UserDB.id == user.get('id')).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Not found")
    if not bcrypt_context.verify(user_verification.password, user_db.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")
    user_db.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_db)
    db.commit()
