from datetime import timedelta

from apis.auth.exceptions import UserAlreadyExistsException
from apis.auth.schemas import Token
from apis.auth.schemas import User as UserSchema
from apis.auth.schemas import UserCreate, UserRead, UserUpdate
from apis.auth.utils import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    update_user,
)
from db.models import User
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing_extensions import Annotated

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()


@router.post("/token")
async def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/profile", response_model=UserRead)
async def get_current_user_details(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.put("/profile", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_current_user_details(
    user: UserSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    db_user = update_user(db, user.username, user)

    return current_user


@router.post(
    "/register",
    response_model=UserRead,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    auth = request.headers.get("Authorization")

    if auth:
        raise HTTPException(
            status_code=400,
            detail="You're already logged in. You can not register an account.",
        )

    try:
        db_user = create_user(
            db,
            user.username,
            user.password,
            user.first_name,
            user.last_name,
            user.phone_number,
        )
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=403,
            detail="Username or phone number already registered.",
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong.",
        )

    return db_user
