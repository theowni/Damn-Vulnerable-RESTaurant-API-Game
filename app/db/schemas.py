# schemas.py
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class UserRole(str, Enum):
    Chef = "Chef"
    Employee = "Employee"
    Customer = "Customer"


class OrderStatus(str, Enum):
    Pending = "Pending"
    Preparing = "Preparing"
    OnTheWay = "OnTheWay"
    Delivered = "Delivered"
    Cancelled = "Cancelled"


class UserBase(BaseModel):
    username: str
    role: UserRole
    first_name: str
    last_name: str
    phone_number: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    image_base64: str


class MenuItemCreate(MenuItemBase):
    pass


class MenuItem(MenuItemBase):
    id: int

    class Config:
        orm_mode = True


class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    date_ordered: datetime = datetime.utcnow()
    status: OrderStatus
    delivery_address: str
    phone_number: str


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = []


class Order(OrderBase):
    id: int
    user_id: int
    items: List[OrderItem] = []

    class Config:
        orm_mode = True
