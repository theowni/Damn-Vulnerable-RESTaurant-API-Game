from apis.users.services.update_user_role_service import (
    router as update_user_role_router,
)
from fastapi import APIRouter

router = APIRouter()
router.include_router(update_user_role_router)
