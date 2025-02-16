from apis.debug.services.get_debug_info_service import router as get_debug_info_router
from fastapi import APIRouter

# debug feature is not included in the OpenAPI schema
# as they are intended for development purposes only
# and should not be exposed to the public
# TODO: remove this router in production
router = APIRouter(include_in_schema=False)
router.include_router(get_debug_info_router)
