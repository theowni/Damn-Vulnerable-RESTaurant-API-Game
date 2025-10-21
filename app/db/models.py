import datetime
import enum

from db.base import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class UserRole(str, enum.Enum):
    CHEF = "Chef"
    EMPLOYEE = "Employee"
    CUSTOMER = "Customer"


class OrderStatus(str, enum.Enum):
    PENDING = "Pending"
    PREPARING = "Preparing"
    ON_THE_WAY = "OnTheWay"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String, unique=True, index=True)
    reset_password_code = Column(String, nullable=True)
    reset_password_code_expiry_date = Column(DateTime, nullable=True)
    referral_code = Column(String, unique=True, index=True, nullable=True)

    orders = relationship("Order", back_populates="user")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    image_base64 = Column(Text)  # Base64-encoded images

    order_items = relationship("OrderItem", back_populates="menu_item")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date_ordered = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    delivery_address = Column(String)
    phone_number = Column(String)
    final_price = Column(Float, default=0.0)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), primary_key=True)
    quantity = Column(Integer)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")


class DiscountCoupon(Base):
    __tablename__ = "discount_coupons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    referrer_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    discount_percentage = Column(Integer)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    used_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    referrer = relationship("User", foreign_keys=[referrer_user_id])
