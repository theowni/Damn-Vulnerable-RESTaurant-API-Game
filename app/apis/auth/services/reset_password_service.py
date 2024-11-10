import secrets
from datetime import datetime, timedelta

from apis.auth.schemas import ResetPasswordData
from apis.auth.utils import send_code_to_phone_number
from db.models import User, UserRole
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 1 week

router = APIRouter()


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
            detail="Invalid username or phone number",
        )
    if user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=400,
            detail="Only customers can reset their password through this feature",
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

    send_code_to_phone_number(user.phone_number, user.reset_password_code)
    return {"detail": "PIN code sent to your phone number"}
