from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class OrderStatus(str, Enum):
    PENDING = "Pending"
    PREPARING = "Preparing"
    ON_THE_WAY = "OnTheWay"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int


class OrderBase(BaseModel):
    delivery_address: str
    phone_number: str


class OrderCreate(OrderBase):
    items: List[OrderItem] = []
    coupon_id: Optional[int] = None


class Order(OrderBase):
    id: int
    user_id: int
    items: List[OrderItem] = []
    status: OrderStatus
    final_price: float

    class Config:
        from_attributes = True
