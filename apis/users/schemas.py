from pydantic import BaseModel


class UserRoleUpdate(BaseModel):
    username: str
    role: str
