from apis.auth.utils import get_current_user
from db.models import User
from fastapi import Depends, HTTPException


class RolesBasedAuthChecker:
    def __init__(
        self,
        required_roles,
    ):
        self.required_roles = required_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.required_roles:
            raise HTTPException(status_code=403, detail="Unauthorized")

        return True
