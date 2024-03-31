from enum import Enum
from typing import List

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


class Order(OrderBase):
    id: int
    user_id: int
    items: List[OrderItem] = []
    status: OrderStatus

    class Config:
        orm_mode = True
