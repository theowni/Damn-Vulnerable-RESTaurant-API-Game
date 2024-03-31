from typing import Optional

from pydantic import BaseModel


class MenuItemCreate(BaseModel):
    name: str
    price: float
    category: str
    image_url: Optional[str] = None
    description: Optional[str] = None


class MenuItem(BaseModel):
    id: int
    name: str
    price: float
    category: str
    description: Optional[str] = None
    image_base64: Optional[str] = None
