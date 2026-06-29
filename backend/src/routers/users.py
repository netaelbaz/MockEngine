"""User registration and login router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src import schemas, crud
from src.auth import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = crud.create_user(db, user_data.email, user_data.password, user_data.first_name, user_data.last_name)
    return schemas.Token(access_token=create_access_token(user.id), first_name=user.first_name, last_name=user.last_name, email=user.email)


@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return schemas.Token(access_token=create_access_token(user.id), first_name=user.first_name, last_name=user.last_name, email=user.email)
