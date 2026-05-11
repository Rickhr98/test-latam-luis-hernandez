from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import logging

from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Management API",
    description="API RESTful para la gestión de usuarios con CRUD completo.",
    version="1.0.0",
)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc: SQLAlchemyError):
    logger.error("Database error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error"},
    )


@app.get("/users", response_model=list[schemas.UserResponse], summary="List all users")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info("List users skip=%s limit=%s", skip, limit)
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.UserResponse, summary="Get a user by ID")
def read_user(user_id: int, db: Session = Depends(get_db)):
    logger.info("Get user id=%s", user_id)
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info("Create user username=%s email=%s", user.username, user.email)
    return crud.create_user(db, user)


@app.put("/users/{user_id}", response_model=schemas.UserResponse, summary="Update an existing user")
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    logger.info("Update user id=%s data=%s", user_id, user.dict(exclude_unset=True))
    return crud.update_user(db, user_id, user)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    logger.info("Delete user id=%s", user_id)
    crud.delete_user(db, user_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
