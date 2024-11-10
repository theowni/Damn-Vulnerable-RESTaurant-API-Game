import secrets
import string

from apis.auth.utils import update_user_password
from config import settings
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

router = APIRouter()


# this is a highly sensitive endpoint used only for admin purposes
# it's excluded from the docs to make it more secure
@router.get(
    "/admin/reset-chef-password",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
def get_reset_chef_password(
    request: Request,
    db: Session = Depends(get_db),
):
    client_host = request.client.host

    # Only requests from the same machine are allowed
    # This endpoint is available only for Chef who is also our server admin!
    if client_host != "127.0.0.1":
        raise HTTPException(
            status_code=403,
            detail="Chef password can be reseted only from the local machine!",
        )

    characters = string.ascii_letters + string.digits + "!@#$%^&*()_-+=;:[]"

    # generate a random password
    new_password = "".join(secrets.choice(characters) for i in range(32))
    update_user_password(db, settings.CHEF_USERNAME, new_password)

    return {"password": new_password}
