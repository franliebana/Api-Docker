from fastapi import APIRouter, Depends, HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserUpdate


# Groups all user-related endpoints under /users.
router = APIRouter(prefix="/users", tags=["users"])

# Creates secure password hashes instead of storing plain-text passwords.
password_hash = PasswordHash.recommended()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
	# Prevent duplicate accounts before inserting the new user.
    existing_user = db.scalar(select(User).where(User.email == user_data.email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    # Store the password hash, never the original password.
    user = User(
        email=user_data.email,
        password_hash=password_hash.hash(user_data.password),
    )
    # Persist the user and load database-generated fields such as id and created_at.
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    # Return users ordered by their database id.
    return list(db.scalars(select(User).order_by(User.id)))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    # Look up a user by its primary key.
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db),) -> User:
    # Look up the user before updating it.
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Convert the Pydantic model to a dictionary, excluding unset fields to allow partial updates.
    update_data = user_data.model_dump(exclude_unset=True)

    # Check that the new email is not already taken by another user before updating it.
    if "email" in update_data and update_data["email"] != user.email:
        # Check for existing users with the same email, excluding the current user.
        existing_user = db.scalar(
            select(User).where(
                User.email == update_data["email"],
                User.id != user_id,
            )
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
        user.email = update_data["email"]

    # Update the password hash if a new password is provided.
    if "password" in update_data:
        user.password_hash = password_hash.hash(update_data["password"])

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    # Look up the user before deleting it.
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()
