from apis.menu.services.create_menu_item_service import (
    router as create_menu_item_router,
)
from apis.menu.services.delete_menu_item_service import (
    router as delete_menu_item_router,
)
from apis.menu.services.get_menu_service import router as get_menu_router
from apis.menu.services.update_menu_item_service import (
    router as update_menu_item_router,
)
from fastapi import APIRouter

router = APIRouter()
router.include_router(create_menu_item_router)
router.include_router(delete_menu_item_router)
router.include_router(get_menu_router)
router.include_router(update_menu_item_router)
