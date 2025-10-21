from datetime import datetime

from apis.auth.utils import RolesBasedAuthChecker, get_current_user
from apis.orders import schemas
from db.models import DiscountCoupon, MenuItem, Order, OrderItem, User, UserRole
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing_extensions import Annotated

router = APIRouter()


@router.post(
    "/orders", response_model=schemas.Order, status_code=status.HTTP_201_CREATED
)
def create_order(
    order: schemas.OrderCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    auth=Depends(RolesBasedAuthChecker([UserRole.CUSTOMER])),
):
    coupon = None
    discount_percentage = 0
    if order.coupon_id:
        coupon = (
            db.query(DiscountCoupon)
            .filter(DiscountCoupon.id == order.coupon_id)
            .first()
        )

        if not coupon or coupon.user_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Coupon not found",
            )

        if coupon.used:
            raise HTTPException(
                status_code=400,
                detail="Coupon has already been used",
            )
        discount_percentage = coupon.discount_percentage

    total_price = 0

    db_order = Order(
        user_id=current_user.id,
        delivery_address=order.delivery_address,
        phone_number=order.phone_number,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Add menu items to the order
    for item in order.items:
        db_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if item.quantity < 1:
            db.rollback()
            raise HTTPException(
                status_code=422,
                detail="Quantity must be greater than 0",
            )
        if not db_item:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Menu item with ID {item.menu_item_id} not found",
            )

        order_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
        )
        db.add(order_item)
        total_price += db_item.price * item.quantity

    db_order.final_price = total_price - (total_price * (discount_percentage / 100))
    db.commit()
    db.refresh(db_order)

    if coupon:
        coupon.used = True
        coupon.used_at = datetime.utcnow()
        db.add(coupon)
        db.commit()

    return db_order
