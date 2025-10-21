import random
import string

from db.models import User
from sqlalchemy.orm import Session


def _generate_code() -> str:
    """Generate an 8-character uppercase alphanumeric code."""
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for _ in range(8))


def get_referral_code(db: Session, db_user: User) -> str:
    """Get or generate a referral code for the user."""
    if db_user.referral_code is None:
        db_user.referral_code = _generate_code()
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user.referral_code
