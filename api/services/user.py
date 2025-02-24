from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..services import auth as auth_services
from ..db.models import User as user_model
from ..schemas import user as user_schemas


def create_user(db: Session, user: user_schemas.UserCreate):
    hashed_password = auth_services.get_password_hash(
        user.password
    )  # Hash the password
    db_user = user_model(
        username=user.username,
        email=user.email,
        password=hashed_password,  # Store the hashed password
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(user_model).filter(user_model.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(user_model).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user: user_schemas.UserUpdate):
    db_user = db.query(user_model).filter(user_model.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.username:
        db_user.username = user.username
    if user.email:
        db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(user_model).filter(user_model.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(db_user)
    db.commit()
    return db_user
