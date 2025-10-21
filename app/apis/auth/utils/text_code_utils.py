import secrets
from datetime import datetime, timedelta

from db.models import User
from sqlalchemy.orm import Session

from .utils import send_code_to_phone_number


def generate_and_send_code_to_user(user: User, db: Session):
    # 4 digits PIN code and 15 minutes expiration shouldn't be bypassed
    # right?
    user.reset_password_code = "".join([str(secrets.randbelow(10)) for _ in range(4)])
    user.reset_password_code_expiry_date = datetime.now() + timedelta(minutes=15)
    db.add(user)
    db.commit()

    success = send_code_to_phone_number(user.phone_number, user.reset_password_code)
    return success
