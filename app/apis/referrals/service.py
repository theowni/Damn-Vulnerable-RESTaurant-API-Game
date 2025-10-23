from typing import List

from apis.auth.schemas import User
from apis.auth.utils import get_current_user
from apis.referrals.schemas import DiscountCouponRead
from apis.referrals.utils import get_referral_code
from db.models import DiscountCoupon
from db.models import User as UserModel
from db.session import get_db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing_extensions import Annotated

router = APIRouter()

# 20% discount on the first order
# for user applying the referral code
REFERRAL_DISCOUNT_PERCENTAGE = 20


class ReferralCodeResponse(BaseModel):
    code: str


class ApplyReferralRequest(BaseModel):
    referral_code: str


class ApplyReferralResponse(BaseModel):
    message: str
    discount: float


@router.get("/referral-code", response_model=ReferralCodeResponse)
async def get_referral_code_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Obtains or creates a referral code for the current user."""
    db_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    code = get_referral_code(db, db_user)

    return ReferralCodeResponse(code=code)


@router.post("/apply-referral", response_model=ApplyReferralResponse)
async def apply_referral_code(
    request: ApplyReferralRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Referrals can be applied by users to receive discounts."""
    referrer = (
        db.query(UserModel)
        .filter(UserModel.referral_code == request.referral_code)
        .first()
    )

    if referrer is None:
        return ApplyReferralResponse(message="Invalid referral code", discount=0.0)

    discount_coupon = DiscountCoupon(
        user_id=current_user.id,
        referrer_user_id=referrer.id,
        discount_percentage=REFERRAL_DISCOUNT_PERCENTAGE,
    )
    db.add(discount_coupon)
    db.commit()

    return ApplyReferralResponse(
        message=f"Referral code {request.referral_code} applied successfully",
        discount=REFERRAL_DISCOUNT_PERCENTAGE,
    )


@router.get("/discount-coupons", response_model=List[DiscountCouponRead])
async def get_discount_coupons(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Retrieve all discount coupons for the current user."""
    coupons = (
        db.query(DiscountCoupon).filter(DiscountCoupon.user_id == current_user.id).all()
    )
    return coupons
