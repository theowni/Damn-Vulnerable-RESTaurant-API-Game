from typing import List

from apis.orders import schemas
from db.models import Order
from db.session import get_db
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/delivery/orders",
    response_model=List[schemas.Order],
    # we exclude this endpoint from the OpenAPI schema because
    # it is not intended for public use!
    include_in_schema=False,
)
def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    This is a dedicated endpoint for delivery services to integrate with
    the Restaurant. Delivery services can use this endpoint to get a list of
    latest orders with their details.
    """
    orders = (
        db.query(Order)
        .order_by(Order.date_ordered.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders
