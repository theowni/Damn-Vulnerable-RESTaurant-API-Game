from apis.auth.utils.text_code_utils import generate_and_send_code_to_user
from db.models import User, UserRole
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from rate_limiting import limiter
from sqlalchemy.orm import Session

router = APIRouter()


class ResetPasswordData(BaseModel):
    username: str


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
def reset_password(
    data: ResetPasswordData,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid username",
        )
    if user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=400,
            detail="Only customers can reset their password through this feature",
        )

    generate_and_send_code_to_user(user, db)
    return {"detail": "PIN code sent to your phone number"}
