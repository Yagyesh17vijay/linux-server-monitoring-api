from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.auth import UserCreate, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_user:
        return {
            "message": "Username already exists"
        }

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "username": new_user.username,
        "user_id": new_user.id
    }

@router.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    password_correct = verify_password(
        user.password,
        existing_user.hashed_password
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token({
        "sub": existing_user.username
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }