from apis.admin.service import router as admin_router
from apis.auth.service import router as auth_router
from apis.healthcheck.service import router as healthcheck_router
from apis.menu.service import router as menu_router
from apis.orders.service import router as orders_router
from apis.users.service import router as users_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(healthcheck_router, prefix="", tags=["healthcheck"])
api_router.include_router(menu_router, prefix="", tags=["menu"])
api_router.include_router(orders_router, prefix="", tags=["orders"])
api_router.include_router(auth_router, prefix="", tags=["auth"])
api_router.include_router(admin_router, prefix="", tags=["admin"])
api_router.include_router(users_router, prefix="", tags=["users"])
