from apis.auth.schemas import User, UserRead
from apis.auth.utils import get_current_user
from fastapi import APIRouter, Depends
from typing_extensions import Annotated

router = APIRouter()


@router.get("/profile", response_model=UserRead)
async def get_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
