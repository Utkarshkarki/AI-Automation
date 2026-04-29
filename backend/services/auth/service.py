"""
services/auth/service.py — Auth service operations (register, login, etc)
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import BaseModel

from services.auth.models import User
from services.auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token

class UserCreate(BaseModel):
    email: str
    password: str
    name: str = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

def register_user(db: Session, user_data: UserCreate) -> TokenResponse:
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.id})
    refresh_token = create_refresh_token(data={"sub": new_user.id})
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

def login_user(db: Session, user_data: UserLogin) -> TokenResponse:
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
