import secrets
from datetime import datetime, timedelta

from apis.auth.exceptions import UserAlreadyExistsException
from apis.auth.schemas import NewPasswordData, ResetPasswordData, Token
from apis.auth.schemas import User as UserSchema
from apis.auth.schemas import UserCreate, UserRead, UserUpdate
from apis.auth.utils import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    update_user,
    update_user_password,
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
    user: UserUpdate,
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


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
def reset_password(
    data: ResetPasswordData,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == data.username).first()

    print(user)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid username or phone number",
        )

    if user.phone_number.replace(" ", "") != data.phone_number.replace(" ", ""):
        raise HTTPException(
            status_code=400,
            detail="Invalid username or phone number",
        )

    # 4 digits PIN code and 15 minutes expiration shouldn't be bypassed
    # right?
    user.reset_password_code = "".join([str(secrets.randbelow(10)) for _ in range(4)])
    user.reset_password_code_expiry_date = datetime.now() + timedelta(minutes=15)
    db.add(user)
    db.commit()

    print(f"PIN {user.reset_password_code} set for {user.username}")

    return {"detail": "PIN code sent to your phone number"}


@router.post(
    "/reset-password/new-password",
    status_code=status.HTTP_200_OK,
)
def set_new_password(
    data: NewPasswordData,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid username or phone number",
        )

    if user.phone_number.replace(" ", "") != data.phone_number.replace(" ", ""):
        raise HTTPException(
            status_code=400,
            detail="Invalid username or phone number",
        )

    if not user.reset_password_code:
        raise HTTPException(
            status_code=400,
            detail="Reset password process was not initiated via /reset-password!",
        )

    if datetime.now() > user.reset_password_code_expiry_date:
        raise HTTPException(
            status_code=400,
            detail="Reset password code expired!",
        )

    if user.reset_password_code != data.reset_password_code:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset password code",
        )

    update_user_password(db, user.username, data.new_password)

    return {}
