from apis.auth.utils import get_current_user
from apis.orders.utils import fetch_order_status_from_delivery_service
from db.models import Order, OrderStatus, User
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing_extensions import Annotated

router = APIRouter()


class OrderStatusResponse(BaseModel):
    status: str
    order_id: int


@router.get("/orders/status/{order_id}", response_model=OrderStatusResponse)
def get_order_status(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    # fetch the order status from a third-party delivery service
    delivery_data = fetch_order_status_from_delivery_service(order_id)
    status_value = delivery_data["status"]

    raw_sql = f"""
        UPDATE orders 
        SET status = '{status_value}'
        WHERE id = {order_id}
    """
    db.execute(text(raw_sql))
    db.commit()

    return OrderStatusResponse(
        order_id=delivery_data["order_id"],
        status=delivery_data["status"],
    )
