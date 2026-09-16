import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse

# Creates a secure password hash verifier instead of comparing plaintext passwords.
password_hash = PasswordHash.recommended()

# Groups all authentication routes under the "auth" tag.
router = APIRouter(tags=["auth"])

# JWT configuration.
# SECRET_KEY is loaded from the environment and, if not provided, it falls back to a temporary development key.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Configures FastAPI to read a JWT from the Authorization header.
bearer_scheme = HTTPBearer()


# Generates a JWT with the user ID and expiration time.
def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Validates the incoming token and returns the authenticated user.
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verifies that the token is valid and signed with the correct key.
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError as exc:
        # If the token is expired, invalid, or malformed, authentication fails.
        raise credentials_exception from exc

    # Finds the user in the database using the ID stored in the JWT.
    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user


# Authenticates a user by email and password and returns a JWT.
@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    user = db.query(User).filter(User.email == login_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verifies the submitted password against the hash stored in the database.
    if not password_hash.verify(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
