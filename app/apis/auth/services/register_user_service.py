from apis.auth.exceptions import UserAlreadyExistsException
from apis.auth.schemas import UserCreate, UserRead
from apis.auth.utils import create_user
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 1 week

router = APIRouter()


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
