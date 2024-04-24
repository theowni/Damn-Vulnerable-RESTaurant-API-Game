from apis.auth.utils import get_current_user, update_user
from apis.users.schemas import UserRoleUpdate
from db import models
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing_extensions import Annotated

router = APIRouter()


@router.put("/users/update_role", response_model=UserRoleUpdate)
async def update_user_role(
    user: UserRoleUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    # Ensure that only employees or the Chef can grant the Employee role
    if current_user.role not in [UserRole.EMPLOYEE, UserRole.CHEF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only employees or the Chef can update user roles!"
        )

    # Prevent assigning the Chef role to other users
    if user.role == UserRole.CHEF:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Only Chef can be assigned the Chef role!"
        )

    # Update the user's role
    db_user = update_user(db, user.username, user)
    return db_user
