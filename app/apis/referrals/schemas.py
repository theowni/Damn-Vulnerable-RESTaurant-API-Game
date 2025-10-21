from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DiscountCouponRead(BaseModel):
    id: int
    discount_percentage: int
    used: bool
    created_at: datetime
    used_at: Optional[datetime]
