"""
services/auth/router.py — FastAPI router for auth endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from services.auth.dependencies import get_db, get_current_user
from services.auth.service import register_user, login_user, UserCreate, UserLogin, TokenResponse
from services.auth.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses 'username' field for the email
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    return login_user(db, user_data)

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "plan_id": current_user.plan_id
    }
