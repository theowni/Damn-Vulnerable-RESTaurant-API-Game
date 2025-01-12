from apis.auth.services.get_profile_service import router as get_profile_router
from apis.auth.services.get_token_service import router as get_token_router
from apis.auth.services.patch_profile_service import router as patch_profile_router
from apis.auth.services.register_user_service import router as register_user_router
from apis.auth.services.reset_password_new_password_service import (
    router as reset_password_new_password_router,
)
from apis.auth.services.reset_password_service import router as reset_password_router
from apis.auth.services.update_profile_service import router as update_profile_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(get_profile_router)
router.include_router(get_token_router)
router.include_router(register_user_router)
router.include_router(update_profile_router)
router.include_router(patch_profile_router)
router.include_router(reset_password_router)
router.include_router(reset_password_new_password_router)
