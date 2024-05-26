from typing import List

from apis.auth.utils import RolesBasedAuthChecker, get_current_user
from apis.orders import schemas
from db.models import MenuItem, Order, OrderItem, User, UserRole
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
    db.commit()
    db.refresh(db_order)

    return db_order


@router.get("/orders", response_model=List[schemas.Order])
def get_orders(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth=Depends(RolesBasedAuthChecker([UserRole.CUSTOMER])),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders


@router.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    auth=Depends(RolesBasedAuthChecker([UserRole.CUSTOMER])),
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order
