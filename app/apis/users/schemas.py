from enum import Enum
from typing import Union

from pydantic import BaseModel, Field


class UserRoleUpdate(BaseModel):
    username: str
    role: str
