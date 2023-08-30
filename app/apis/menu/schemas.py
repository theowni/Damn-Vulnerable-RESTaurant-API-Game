from datetime import datetime
from enum import Enum
from typing import List, Optional

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
